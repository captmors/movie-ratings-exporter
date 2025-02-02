import json
from src.config import ROOT_DIR, config
from src.utils.logger import logger
from typing import Any, Tuple, List
from src.utils.browser import Browser
from src.utils.ratings import MovieRating, main as get_ratings
from loguru import logger
from tabulate import tabulate
import re
from rapidfuzz import fuzz
from playwright.sync_api import Locator, Page


def ask_for_cookies():
    print("Cookies for Criticker are not set. Let's add them!")
    
    while True:
        try:
            cookies_input = input("Enter your cookies: ")
            cookies = json.loads(cookies_input) 

            if not isinstance(cookies, list):
                raise ValueError("Input must be a list of cookies")

            config.COOKIES_FOR_CRITICKER.extend(cookies)

            save_cookies_to_env()
            print("Cookies have been saved successfully!")
            break

        except json.JSONDecodeError:
            print("Invalid JSON format. Please try again.")
        except ValueError as e:
            print(e)

def save_cookies_to_env():
    env_path = ROOT_DIR / ".env"
    with open(env_path, "a") as env_file:
        env_file.write(f"\nCOOKIES_FOR_CRITICKER={json.dumps(config.COOKIES_FOR_CRITICKER)}")
        

def get_title_year_from_row(row: Locator):
    def parse_title_year(text: str) -> Tuple[str, str]:    
        match = re.search(r"(.+) \((\d{4})\)", text)
        if match:
            return match.group(1).strip(), int(match.group(2))
        return None, None
    
    text = row.locator('.titlerow_mid > .titlerow_name > a').text_content()
    found_title, found_year = parse_title_year(text)
    
    if not found_title or not found_year:
        logger.error(f"Failed to parse movie card name: {text}")
                    
    return found_title, str(found_year)


def interactive_choice(target: str, pretender_rows: List[Locator]) -> Locator:
    """ Allows the user to select the correct movie from the list of options """
    if not pretender_rows:
        return None
    
    logger.info(f"(Choice) Rating the film: {target}")
    for idx, p_r in enumerate(pretender_rows):
        title, year = get_title_year_from_row(p_r)        
        logger.info(f"{idx + 1}. {title} ({year})")
    
    while True:
        choice = input("Enter the number of the correct option or 'q' to exit: ")
        if choice.lower() == 'q':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(pretender_rows):
            return pretender_rows[int(choice) - 1]


def confirm_change(field_name, existing_value, new_value):
    if existing_value and existing_value != new_value:
        confirm = input(f"{field_name}: current {existing_value}. Change to {new_value}? (y/n): ")
        return confirm.lower() == 'y'
    return True


def rate_movie(selected_row: Locator, page: Page, rating: MovieRating):
    """Rates a movie, fills out the form, and saves it"""
    
    # click rate btn
    selected_row.wait_for() 
    already_rated_rate_card_btn = selected_row.locator('.rate_card a')
    never_rated_rate_card_btn = selected_row.locator('.psi_card button')
    assert (already_rated_rate_card_btn.count() + never_rated_rate_card_btn.count() == 1), f"already_rated_rate_card_btn == {already_rated_rate_card_btn.count()} never_rated_rate_card_btn == {never_rated_rate_card_btn.count()}"    
    
    if already_rated_rate_card_btn.count() == 1:
        already_rated_rate_card_btn.wait_for()
        logger.debug(f"Already rated btn: {already_rated_rate_card_btn.inner_html()}")
        page.goto(already_rated_rate_card_btn.get_attribute('href'))
    else:
        never_rated_rate_card_btn.wait_for()
        logger.debug(f"Never rated btn: {never_rated_rate_card_btn.inner_html()}")
        never_rated_rate_card_btn.click()

    # pass rating dialog 
    rating_dialog = page.locator("#modal_dialog_rating")
    rating_dialog.wait_for()
    
    rating_input = rating_dialog.locator('.textinput.ratinginput')
    rating_input.wait_for()
    new_rating = str(10 * int(rating.rating))
    if confirm_change("Rating", rating_input.input_value(), new_rating):
        rating_input.fill(new_rating)
    
    date_input = rating_dialog.locator('#datepicker_watchdate')
    date_input.wait_for()
    if confirm_change("Watch date", date_input.input_value(), rating.rated_at):
        formatted_date = rating.rated_at.strftime("%d %b %Y")
        date_input.fill(formatted_date)
        date_input.press('Enter')
    
    save_button = rating_dialog.locator(".primary.submit_rating")
    save_button.wait_for()
    save_button.click()
    
    logger.info(f"Movie {rating.title} ({rating.year}) successfully rated!")