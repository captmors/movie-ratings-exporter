from core.criticker import load_ratings_to_criticker
from src.core.taste_io import load_ratings_to_taste_io
from src.utils.logger import setup_logger


if __name__ == '__main__':
    setup_logger()
    
    load_ratings_to_criticker()
    load_ratings_to_taste_io()
    