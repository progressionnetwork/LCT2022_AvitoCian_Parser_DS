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

def get_content_page(html):
    """Функция сбора данных"""
    soup = BeautifulSoup(html, 'lxml') 
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    # rooms,m2,floor,depth,street,metro,m2_price,price
    headers = ['name', 'city','area','link','price']
    with open('dataset.csv', mode='w', encoding='utf-8', errors='ignore', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        for block in blocks:
            #try:
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
            description = block.find('div', class_=re.compile('iva-item-description')).get_text(strip=True) # description
            print(description)
            link = 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href') # link
            m2_price = block.find('span', class_=re.compile('price-noaccent')).get_text(strip=True).replace('₽ за м²', '').replace('\xa0', '') # m2_price
            price = block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace('\xa0', '') # price

            parsed = [
                rooms,
                m2,
                floor,
                depth,
                area,
                metro_name,
                m2_price,
                price,
                #link
            ]
            writer.writerow(parsed)
            # except:
            #     print("Error while row writing.. skip")

    # сбор данных с страницы
    data = []
    for block in blocks:
        data.append({
            "Наименование": block.find('h3', class_=re.compile('title-root')).get_text(strip=True),
            'Цена': block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace(
                '\xa0', ''),
            'Город': block.find('a', class_=re.compile('link-link')).get('href').split('/')[1],
            'Район': block.find('div', class_=re.compile('geo-root')).get_text(strip=True),
            'Ссылка': 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href'),
        })
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
    browser = webdriver.Firefox(executable_path=r"D:\Projects\real_estate_parsing-master\real_estate_parsing-master\geckodriver.exe",
        options=options)
    browser.get(url)
    html = browser.page_source
    pages = 2 #get_pages(html)  #определяем количество страниц выдачи
    data_list_pages = []
    for page in range(1, pages + 1):
        link = url + f'&p={page}'
        try:
            browser.get(link)
            time.sleep(1)
            html = browser.page_source
            parsed_page = get_content_page(html)
            #print(parsed_page)
            #print('==='*20)
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
    with open('test.html', encoding='utf-8', errors='ignore') as f:
        html = f.readlines()
    html = ''.join(html).encode('utf-8')
    get_content_page(html)
    sys.exit()
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