from pathlib import Path
import re
import pandas as pd
from pydantic import BaseModel, field_validator, model_validator, root_validator
from datetime import datetime
from typing import List, Optional, Tuple
from loguru import logger
from tabulate import tabulate

from src.config import IMDB_RATINGS_PATH, KINOPOISK_RATINGS_PATH


class MovieRating(BaseModel):
    """Schema for unified movie rating format"""
    title: str
    rating: str 
    year: str
    rated_at: datetime

    _year_invalid: bool

    @field_validator('rating')
    def validate_rating(cls, v):
        if not 1 <= int(v) <= 10:
            raise ValueError('Rating must be between 1 and 10')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @model_validator(mode='after')
    def validate_year(self):
        if not re.match(r'^\d{4}$', self.year):
            self._year_invalid = True
            logger.warning(f"Invalid year format: {self.year}\nEntry: {self.model_dump_json()}")

        return self


class RatingsParser:
    def __init__(self, imdb_path: Optional[Path] = None, kinopoisk_path: Optional[Path] = None):
        self.imdb_path = imdb_path
        self.kinopoisk_path = kinopoisk_path

    def parse_imdb(self) -> Optional[List[MovieRating]]:
        """Parse IMDB ratings CSV file"""
        if self.imdb_path is None:
            logger.warning("IMDB path is not set")
            return None

        if not self.imdb_path.exists():
            logger.error(f"IMDB file not found: {self.imdb_path}")
            return None

        try:
            df = pd.read_csv(self.imdb_path)
            ratings = []
            invalid_rows = []

            for _, row in df.iterrows():
                if pd.notna(row.get('Original Title')) and pd.notna(row.get('Your Rating')):
                    try:
                        rating = MovieRating(
                            title=row['Original Title'],
                            rating=str(round(float(row['Your Rating']))),
                            year=str(row['Year']),
                            rated_at=datetime.strptime(row['Date Rated'], '%Y-%m-%d')
                        )
                        ratings.append(rating)
                    except Exception as e:
                        invalid_rows.append((row.to_dict(), str(e)))
                else:
                    reason = "Missing required fields"
                    invalid_rows.append((row.to_dict(), reason))

            for row_data, reason in invalid_rows:
                logger.error(f"\n[Error] {reason}\n[Row] {row_data}")

            logger.info(f"Successfully parsed {len(ratings)} IMDB ratings")
            logger.info(f"Unsuccessfully parsed {len(invalid_rows)} IMDB ratings")
            return ratings

        except Exception as e:
            logger.error(f"Error parsing IMDB file: {str(e)}")
            return None


    def parse_kinopoisk(self) -> Optional[List[MovieRating]]:
        """Parse Kinopoisk ratings CSV file"""
        if self.kinopoisk_path is None:
            logger.warning("Kinopoisk path is not set")
            return None

        if not self.kinopoisk_path.exists():
            logger.error(f"Kinopoisk file not found: {self.kinopoisk_path}")
            return None

        try:
            df = pd.read_csv(self.kinopoisk_path)
            ratings = []
            invalid_rows = []

            for _, row in df.iterrows():
                if pd.notna(row.get('Name')) and pd.notna(row.get('Rating_10')):
                    try:
                        rating = MovieRating(
                            title=row['Name'],
                            rating=str(round(float(row['Rating_10']))),
                            year=str(row['Year']),
                            rated_at=datetime.strptime(row['Date'], '%Y-%m-%d')
                        )
                        ratings.append(rating)
                    except Exception as e:
                        invalid_rows.append((row.to_dict(), str(e)))
                else:
                    reason = "Missing required fields"
                    invalid_rows.append((row.to_dict(), reason))

            for row_data, reason in invalid_rows:
                logger.error(f"\n[Error] {reason}\n[Row] {row_data}")

            logger.info(f"Successfully parsed {len(ratings)} Kinopoisk ratings")
            logger.info(f"Unsuccessfully parsed {len(invalid_rows)} Kinopoisk ratings")
            return ratings

        except Exception as e:
            logger.error(f"Error parsing Kinopoisk file: {str(e)}")
            return None


class RatingsManager:
    def join_ratings(ratings_lists: List[List[MovieRating]]) -> List[MovieRating]:
        """
        Join multiple rating lists based on title and year
        Returns unique ratings (if same title+year exists in multiple lists, takes the first occurrence)
        """
        if not ratings_lists:
            return []

        # Create dictionary with (title, year) as key
        unique_ratings = {}
        for ratings in ratings_lists:
            for rating in ratings:
                key = (rating.title.lower(), rating.year)
                if key not in unique_ratings:
                    unique_ratings[key] = rating

        return list(unique_ratings.values())

    def print_ratings(ratings: List[MovieRating]) -> None:
        """Print ratings in a nice tabulated format"""
        logger.info(f"Total ratings: {len(ratings)}")

        if not ratings:
            logger.warning("No ratings to display")
            return

        data = []
        for r in ratings:
            data.append({
                'Title': r.title,
                'Year': r.year,
                'Rating': r.rating,
                'Rated At': r.rated_at.strftime('%Y-%m-%d')
            })

        print("\n" + tabulate(
            data,
            headers='keys',
            tablefmt='grid',
            showindex=True
        ))


def main() -> List[MovieRating]:
    """Parse and merge two csv's if present in config"""
    
    parser = RatingsParser(
        imdb_path=IMDB_RATINGS_PATH,
        kinopoisk_path=KINOPOISK_RATINGS_PATH
    )

    imdb_ratings = parser.parse_imdb()
    kp_ratings = parser.parse_kinopoisk()

    all_ratings = []
    if imdb_ratings and kp_ratings:
        # Join ratings
        logger.info(f"Total length before merging: imdb + kp = {len(imdb_ratings)} + {len(kp_ratings)} = {len(imdb_ratings) + len(kp_ratings)}")
        all_ratings = RatingsManager.join_ratings([imdb_ratings, kp_ratings])
        logger.info(f"Total length after merging: {len(all_ratings)} ({len(all_ratings) - len(imdb_ratings) + len(kp_ratings)})")
        
    return all_ratings


if __name__ == "__main__":
    main()
    