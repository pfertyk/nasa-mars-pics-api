import os
import pathlib


BASE_DIR = pathlib.Path(__file__).parent.parent

DATABASE_URL = os.environ.get('DATABASE_URL')
NASA_API_KEY = os.environ.get('NASA_API_KEY', 'DEMO_KEY')

ROVER_URL = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/'
