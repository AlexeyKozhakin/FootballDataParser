#Скрипт для сохранения страниц
import pandas as pd
from soccer_stats_scraper import save_pages_to_html


save_pages_to_html(directory='data/LK/2021_2022/',file_game_id='data/games21_22LK_lost.csv')