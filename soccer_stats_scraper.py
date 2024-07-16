from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup as BS
import os


def save_dataset(directory='data/championship', file_id='data/games.csv', dataset_file='data/dataset.csv'):
    # Чтение данных из файла CSV
    df = pd.read_csv(file_id)
    # Преобразование данных в список
    ids = df['Game ID'].tolist()
    dataset = {}
    i = 0
    for id in ids:
        i += 1
        print(f'line {i}')
        file_name = f'{id}.html'
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            soup_time_goal = file.read()
            soup_time_goal = BS(soup_time_goal, "html.parser")

        file_name = f'form_teams{id}.html'
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            soup_stat_param = file.read()
            soup_stat_param = BS(soup_stat_param, "html.parser")

        line_dataset = get_line_for_dataset(id, soup_time_goal, soup_stat_param)
        if dataset == {}:
            dataset = line_dataset
        else:
            for key in line_dataset:
                dataset[key] += line_dataset[key]
    df = pd.DataFrame(dataset)
    df.to_csv(dataset_file, encoding='utf-8', index=False)
def save_pages_to_html(directory='data/championship/',file_game_id='games_id.csv'):
    # Чтение данных из файла CSV
    df = pd.read_csv(file_game_id)
    # Преобразование данных в список
    ids = df['Game ID'].tolist()
    i = 0
    start_time = time.time()
    for id in ids:
      i+=1
      print(f'line {i}')
      save_page_html(directory,id, forms=False)
      save_page_html(directory,id, forms=True)
    # Замеряем время окончания выполнения скрипта
    end_time = time.time()

    # Вычисляем и выводим время выполнения
    execution_time = end_time - start_time
    print(f"Время выполнения скрипта: {execution_time:.2f} секунд")

def save_page_html_requests(id_game, forms = False):
    if not forms:
        link = f'https://soccer365.ru/games/{id_game}/'
        file_name = f'{id_game}.html'
    else:
        link = f'https://soccer365.ru/games/{id_game}/&tab=form_teams'
        file_name = f'form_teams{id_game}.html'

    # Получаем полный HTML страницы
    get_page_html = requests.get(link)
    page_html = get_page_html.text
    # Сохраняем HTML в файл
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(page_html)

def get_list_games_id(soup):
    # Ищем тэг <a> с классом "game_link"
    blocks_with_id = soup.find_all('a', class_='game_link')
    # Достаем значение из dt-id attribute
    list_games_id = []
    for block_with_id in blocks_with_id:
      game_id = block_with_id.get('dt-id')
      list_games_id.append(game_id)
    return list_games_id
def create_directory(directory):
    # Проверка наличия каталога
    if not os.path.exists(directory):
        # Создание каталога
        os.makedirs(directory)
        print(f"Каталог '{directory}' успешно создан.")
    else:
        print(f"Каталог '{directory}' уже существует.")
def save_file_id_games(directory='data',file='games_id.csv', url_games='https://soccer365.ru/competitions/12/2018-2019/results/'):
    create_directory(directory)
    html_games=requests.get(url_games)
    soup = BS(html_games.text,"html.parser")
    list_games_id = get_list_games_id(soup)
    # Преобразование списка в DataFrame
    print(len(list(list_games_id)))
    df = pd.DataFrame(list_games_id, columns=['Game ID'])
    # Запись DataFrame в файл CSV
    df.to_csv(directory+'/'+file, index=False)  # index=False говорит, что индексы не нужно сохранять в файл

def save_page_html(directory,id_game, forms = False):
    create_directory(directory)
    if not forms:
        link = f'https://soccer365.ru/games/{id_game}/'
        file_name = f'{id_game}.html'
    else:
        link = f'https://soccer365.ru/games/{id_game}/&tab=form_teams'
        file_name = f'form_teams{id_game}.html'

    # Установите параметры для Firefox
    options = Options()
    options.headless = True  # Запуск в фоновом режиме

    # Укажите путь к исполняемому файлу Firefox
    options.binary_location = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'  # Замените на ваш путь


    # Путь к geckodriver
    geckodriver_path = 'C:\\Users\\alexey\\Downloads\\geckodriver-v0.34.0-win32\\geckodriver.exe'

    # Запуск браузера
    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)

    # Переход на страницу
    driver.get(link)

    # # Ждем полной загрузки страницы (необязательно, зависит от страницы)
    # time.sleep(5)

    # Получаем полный HTML страницы
    page_html = driver.page_source
    file_path = os.path.join(directory, file_name)
    # Сохраняем HTML в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(page_html)

    # Закрываем браузер
    driver.quit()

def get_score_from_soup(soup, side = None):
    if side == None:
      raise ValueError("Не задана сторона откуда берем данные")
    else:
      data_ht = soup.find(class_='live_game '+side)
      goals_ht = data_ht.find(class_='live_game_goal')
      #print(goals_ht)
      return goals_ht.text.strip()

def get_both_score(soup):
    goals_ht = get_score_from_soup(soup, side = 'left')
    goals_at = get_score_from_soup(soup, side = 'right')
    return goals_ht, goals_at

def get_line_for_dataset(id, soup_time_goal, soup_stat_param):
    dataset_line = {}
    soup = soup_time_goal
    dataset_line['id'] = [id]
    dataset_line['Время гола'] = time_goal(soup)
    sc_h, sc_g = get_both_score(soup)
    dataset_line['sc_h'] = [sc_h]
    dataset_line['sc_g'] = [sc_g]
    teams = get_name_teams(soup)
    soup = soup_stat_param
    dataset_line.update(get_stat_param_tables(soup_stat_param))
    dataset_line.update({'team_home':[teams[0]],'team_guest':[teams[1]]})
    return dataset_line

def extract_rest_time(time):
    tim1,tim2=time.split(' ')
    if '(' in tim1:
        return int(tim1[1:-1])
    else:
        return int(tim2[1:-1])

# put your python code here
def extract_game_count_from_string(str):
    if str[-1]=='%':
        return str[0]
    else:
        return str[-1]


def get_name_teams(soup):
    match_info = soup.find_all(class_="block_header bkcenter")
    team_h = soup.find(class_="live_game_ht")
    team_g = soup.find(class_="live_game_at")
    return team_h.text.strip(), team_g.text.strip()

def time_goal(soup):
    # Ищем все события домашней команды
    events_ht = soup.find_all(class_='event_ht')
    # Ищем все события домашней команды
    events_at = soup.find_all(class_='event_at')
    # Парсим все времена когда происходили события
    events_time = soup.find_all(class_='event_min')
    flag = True
    for event_ht,event_at,event_time in zip(events_ht,events_at,events_time):
        if event_ht.find_all(class_='event_ht_icon live_goal') or \
          event_at.find_all(class_='event_ht_icon live_pengoal') or\
          event_at.find_all(class_='event_at_icon live_goal') or \
          event_at.find_all(class_='event_at_icon live_pengoal'):
          flag = False
          break
    if flag:
        return ['-']
    else:
        return [event_time.text[:-1]]

def get_stat_param_tables(soup):
    tables = soup.find_all(class_="tablesorter")
    soup = tables[0]
    # Найдем все строки в теле таблицы
    rows = soup.find('tbody').find_all('tr')
    # Возьмем 5-ую строчку
    #в которой расположена информация о Забитых голах командами
    table={}
    for row in rows:
      cells = row.find_all('td')
      # Extract text from the cells
      left_value = cells[0].get_text(strip=True)
      name_param = cells[1].get_text(strip=True)
      right_value = cells[2].get_text(strip=True)
      if name_param!='Матчи':
          if '%' in left_value:
              left_value = extract_game_count_from_string(left_value)
          if '%' in right_value:
              right_value = extract_game_count_from_string(right_value)
          if ')' in left_value:
              left_value = extract_rest_time(left_value)
          if ')' in right_value:
              right_value = extract_rest_time(right_value)
          table[name_param+'-home'] = [left_value]
          table[name_param+'-guest'] = [right_value]
    # берем данные из таблицы 2
    soup = tables[1]
    # Найдем все строки в теле таблицы
    rows = soup.find('tbody').find_all('tr')
    for row in rows:
      cells = row.find_all('td')
      # Extract text from the cells
      left_value = cells[0].get_text(strip=True)
      name_param = cells[1].get_text(strip=True)
      right_value = cells[2].get_text(strip=True)
      table[name_param+'-home'] = [left_value]
      table[name_param+'-guest'] = [right_value]
    return table