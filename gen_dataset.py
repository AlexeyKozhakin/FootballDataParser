import pandas as pd
from bs4 import BeautifulSoup as BS
from soccer_stats_scraper import save_dataset
import os



save_dataset(directory='data/LK/2021_2022/',file_id='data/games21_22LK.csv', dataset_file='data/dataset21_22LK.csv')