from typing import Any, Tuple, List
from src.utils.browser import Browser
from src.utils.ratings import MovieRating, main as get_ratings
from loguru import logger
from tabulate import tabulate
from rapidfuzz import fuzz
from src.config import config
from src.utils.utils import ask_for_cookies, get_title_year_from_row, interactive_choice, rate_movie


def load_ratings_to_criticker():
    if not config.COOKIES_FOR_CRITICKER:
        logger.error("Cookies for Criticker are not set. Please set them in .env")
        ask_for_cookies()
        
    logger.info("Initializing browser session")
    with Browser() as browser:
        browser.setup()
        
        page = browser.page
        page.goto("https://www.criticker.com/")
        
        rated = []
        not_rated = []
        
        ratings = get_ratings()
        logger.info(f"Loaded {len(ratings)} ratings to process")
        
        for rating in ratings:
            try:
                logger.debug(f"Searching for: {rating.title} ({rating.year})")
                search_box = page.locator(".i_searchbox.films")
                search_box.wait_for()
                search_box.fill(rating.title)
                search_box.press("Enter")

                search_results = page.locator('.sr_results_div')
                search_results.wait_for()
                    
                if not search_results.count():
                    logger.warning(f"{rating.title} not found.")
                    not_rated.append(rating)
                    continue
                
                rows = search_results.locator('> .titlerow')
                selected_row = None
                pretender_rows = []

                for i in range(rows.count()):
                    row = rows.nth(i)
                    found_title, found_year = get_title_year_from_row(row)
                    logger.debug(f"Found: {found_title} ({found_year})")
                    
                    title_match = fuzz.ratio(found_title.lower(), rating.title.lower())
                    titles_equal = found_title == rating.title
                    titles_alike = title_match > 70
                    if not titles_equal and titles_alike:
                        logger.debug(f"Alike titles found!\nTitle match:{title_match}/100\nimported:{rating.title}\non site: {found_title}")
                    
                    years_equal = found_year == rating.year

                    if titles_equal and years_equal or \
                       titles_alike and years_equal:
                            
                        logger.debug(f"Exact match found: {found_title} ({found_year})")
                        selected_row = row
                        break
                    
                    elif titles_alike and not years_equal or \
                         not titles_alike and years_equal:
                            
                        pretender_rows.append(row)
                        continue
                    
                    else:
                        continue

                # --------- analyze results from the first page ---------
                if selected_row:
                    rate_movie(selected_row, page, rating)
                    rated.append(rating)
                    
                elif pretender_rows:
                    choice = interactive_choice(f"{rating.title} ({rating.year})", pretender_rows)
                    if choice:                        
                        rate_movie(choice, page, rating)
                        rated.append(rating)
                    else:
                        not_rated.append(rating)
                        
                else:
                    not_rated.append(rating)  
                        
            except Exception as e:
                logger.error(f"Error searching for: {rating.title} ({rating.year})\n{e}")
            
        logger.info(f"Total Rated: {len(rated)}")
        logger.info(f"Total Not Rated: {len(not_rated)}")
        
        logger.info("Movies not rated:")
        logger.info(tabulate(
            [(r.title, r.year) for r in not_rated], 
            headers=["Title", "Year"], 
            tablefmt="grid"
        ))
