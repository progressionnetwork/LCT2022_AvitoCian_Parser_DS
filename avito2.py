import csv
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas
from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
# pip install openpyxl

"""Парсер торговой площидки Avito через Selenium"""


def get_pages(html):
    """определяем количеоств страниц выдачи"""
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('div', class_=re.compile('pagination-root')).find_all('span', class_=re.compile('pagination-item'))[-2].text
    print(f'Найдено страниц выдачи: {pages}')
    return int(pages)


def metro_split(s):
    head = s.rstrip('0123456789-')
    tail = s[len(head):]
    return head, tail

def text_num_split(item):
    name = ''
    for index, letter in enumerate(item, 0):
        if not letter.isdigit():
            name = name + letter
    return name.replace('–', '').replace('мин.', '').replace(' ', '')


def metro_split(item):
    name = ''
    for index, letter in enumerate(item, 0):
        if not letter.isdigit():
            name = name + letter
        else:
            break
        dist = item.split(name)
    return name, dist

def get_metro_distance(location):
    elements = location.split(' ')
    multiplier = 1
    for i in range(len(elements)):
        if elements[i].strip() in ['м,', 'км,']:
            if elements[i].startswith('км'):
                multiplier = 1000
            distance_str = elements[i-1].replace(',', '.')
            return float(distance_str) * multiplier
    return 0

import base64
def get_content_page(html):
    """Функция сбора данных"""
    soup = BeautifulSoup(html, 'lxml') #.encode("utf-8") .text.encode('utf8').decode('ascii', 'ignore')
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    # rooms,m2,floor,depth,street,metro,m2_price,price

    try:
        with open('dataset.csv', mode='a', encoding="utf-8", errors='ignore', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for block in blocks:
                try:
                    market_price = 0
                    market_query = 0
                    obj_name = block.find('h3', class_=re.compile('title-root')).get_text(strip=True) # name
                    obj_data = obj_name.split(', ')
                    rooms = obj_data[0][0]
                    m2 = obj_data[1].replace(' м²','').replace(',','.')
                    floor_data = obj_data[2]
                    if len(floor_data) < 1:
                        continue
                    floor = obj_data[2].split('/')[0].replace('\xa0','')
                    depth = obj_data[2].split('/')[1].replace('\xa0эт.','')            
                    metro = block.find('div', class_=re.compile('geo-georeferences')).get_text(strip=True)
                    metro_name, metro_dist = metro_split(metro)
                    metro_dist = metro_dist[1].split('–')[0].replace('мин.','')
                    #print(metro, metro_name, metro_dist)
                    #print(obj_name, 'rooms', rooms, 'm2', m2, 'floor', floor, 'depth', depth)
                    area = block.find('div', class_=re.compile('geo-root')).get_text(strip=True) # area

                    span_data = block.find('span', class_=re.compile('SnippetBadge-title-afjYB')) # market_price
                    if span_data:
                        span_data = span_data.get_text(strip=True)
                        if span_data == 'Высокий спрос':
                            market_query = 1
                        if span_data == 'Рыночная цена':
                            market_price = 1

                    description = block.find('div', class_=re.compile('iva-item-description')).get_text(strip=True) # description
                    sample_string_bytes = description.encode("utf-8")  
                    base64_bytes = base64.b64encode(sample_string_bytes)
                    base64_string = base64_bytes.decode("ascii")
                    link = 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href') # link
                    id = link.split('_')[-1:]
                    m2_price = block.find('span', class_=re.compile('price-noaccent')).get_text(strip=True).replace('₽ за м²', '').replace('\xa0', '') # m2_price
                    price = block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace('\xa0', '') # price

                    parsed = [
                        id,
                        obj_name,
                        rooms,
                        m2,
                        floor,
                        depth,
                        area,
                        metro_name,
                        metro_dist,
                        market_price,
                        market_query,
                        m2_price,
                        price,
                        #link,
                        base64_string
                    ]
                    writer.writerow(parsed)
                except:
                    print("Error while row writing.. skip")
    except:
            print("Error while writing csv file")

    # сбор данных с страницы
    data = []
    for block in blocks:
        link = 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href') # link
        id = link.split('_')[-1:]                    
        data.append('id':id)
    #     data.append({
    #         "Наименование": block.find('h3', class_=re.compile('title-root')).get_text(strip=True),
    #         'Цена': block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace(
    #             '\xa0', ''),
    #         'Город': block.find('a', class_=re.compile('link-link')).get('href').split('/')[1],
    #         'Район': block.find('div', class_=re.compile('geo-root')).get_text(strip=True),
    #         'Ссылка': 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href'),
    #     })
    return data


def parser(url):
    """Основная функция, сам парсер"""
    options = webdriver.FirefoxOptions()
    #options.add_argument("user-agent=Mozilla/5.0") # headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--log-level=3')
    #options.add_argument("--headless")  #режим без запуска браузера

    # укажите путь до драйвера
    #service = Service()
    browser = webdriver.Firefox(executable_path=r"geckodriver.exe",
        options=options)
    browser.get(url)
    html = browser.page_source
    #pages = 100 
    pages = get_pages(html)  #определяем количество страниц выдачи
    data_list_pages = []
    for page in range(1, pages + 1):
        link = url + f'&p={page}'
        try:
            browser.get(link)
            time.sleep(1)
            html = browser.page_source
            parsed_page = get_content_page(html)
            #print(parsed_page)
            print('==='*20)
            data_list_pages.extend(parsed_page)
            print(f'Парсинг страницы {page} завершен. Собрано {len(data_list_pages)} позиций')
        except Exception as ex:
            print(f'Не предвиденная ошибка: {ex}')
            browser.close()
            browser.quit()
    print('Сбор данных завершен.')
    return data_list_pages


def save_exel(data):
    """Функция сохранения в файл"""
    dataframe = pandas.DataFrame(data)
    df = dataframe.drop_duplicates(['Ссылка'])
    with open('file.csv', 'a') as file:
        file.write('numrows numcols note\n')
        df.to_csv(file, sep=',', encoding='utf-8', header=False, index=False, errors='ignore')
    # writer = pandas.ExcelWriter(f'data_avito.xlsx') 
    # df.to_excel(writer, 'data_avito')
    # writer.save()
    print(f'Удаление дубликатов...\nСобрано {len(df)} объявлений')
    print(f'Данные сохранены в файл "data_avito.xlsx"')


if __name__ == "__main__":
    # with open('test.html', encoding='utf-8', errors='ignore') as f:
    #     html = f.readlines()
    # html = ''.join(html).encode('utf-8')
    # get_content_page(html)
    #sys.exit()
    # headers = ['name', 'city','area','link','price']    
    # with open('dataset.csv', mode='w', encoding='utf-8', errors='ignore') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=",")
    #     writer.writerow(headers)
    #     csvfile.close()
    #url = input('Введите ссылку на раздел, с заранее выбранными характеристиками (ценовой диапазон и тд):\n')
    #url = 'https://www.avito.ru/bashkortostan?bt=1&f=ASgCAgECAUXGmgwZeyJmcm9tIjoxMTAwMCwidG8iOjEyMDAwfQ&i=1&q=%D0%B2%D0%B5%D0%BB%D0%BE%D1%81%D0%B8%D0%BF%D0%B5%D0%B4&s=104'
    url = 'https://www.avito.ru/moskva/kvartiry/prodam/vtorichka-ASgBAgICAkSSA8YQ5geMUg?context=H4sIAAAAAAAA_0q0MrSqLraysFJKK8rPDUhMT1WyLrYyNLNSKk5NLErOcMsvyg3PTElPLVGyrgUEAAD__xf8iH4tAAAA&f=ASgBAQICAkSSA8YQ5geMUgFAyggkglmAWQ'
    print('Запуск парсера...')
    save_exel(parser(url))