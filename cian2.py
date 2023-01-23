import csv
import os
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
    #soup = BeautifulSoup(html, 'lxml')
    #pages = soup.find('div', class_=re.compile('pagination-root')).find_all('span', class_=re.compile('pagination-item'))[-2].text
    pages = 100
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
    soup = BeautifulSoup(html, 'lxml') 
    n = 0
    #blocks = soup.find_all('div', class_=re.compile('--'))
    blocks = soup.select('article[data-name="CardComponent"]')
    for block in blocks:
        try:
            with open('dataset.csv', mode='a', encoding="utf-8", errors='ignore', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                for block in blocks:
                    try:                        
                        metroname = ''
                        addrname = ''
                        pricename = ''
                        m2pricename = ''
                        descrname = ''

                        obj_name = block.select('span[data-mark="OfferTitle"]')
                        name = block.find('span', class_=re.compile('--color_primary_100--')).get_text(strip=True)
                        link = block.find('a', class_=re.compile('--link--eoxce'))['href']
                        print(link)

                        id = link.split('/')[5]
                        print(id)
                        
                        buildername = block.find('span', class_=re.compile('--color_current_color--')).get_text(strip=True)
                        print(buildername)

                        obj_sub = block.select('div[data-mark="OfferSubtitle"]')
                        subname = block.find('span', class_=re.compile('--color_black_100--')).get_text(strip=True)
                        print(subname)

                        try:
                            obj_jk = block.select('div[data-name="ContentRow"]')
                            jkname = block.find('a', class_=re.compile('--jk--')).get_text(strip=True)
                            print(jkname)
                        except:
                            print('jk: ---')

                        metro_obj = block.select('div[data-name="SpecialGeo"]')
                        for item in metro_obj:
                            metroname += item.get_text(strip=True)
                        print(metroname)

                        addr_obj = block.select('div[data-name="GeneralInfoSectionRowComponent"]')
                        for item in addr_obj:   
                            addrname = ''
                            try:       
                                addrname = item.find('div', class_=re.compile('--labels--')).get_text(strip=True)
                            except:
                                pass
                            addrname = addrname.strip()
                            if len(addrname) > 10:
                                break
                        print(addrname)
                        
                        price_obj = block.select('span[data-mark="MainPrice"]')
                        for item in price_obj:
                            pricename += item.get_text(strip=True)
                        print(pricename)
                        
                        m2price_obj = block.select('p[data-mark="PriceInfo"]')
                        for item in m2price_obj:
                            m2pricename += item.get_text(strip=True)
                        print(m2pricename)

                        descr_obj = block.select('div[data-name="Description"]')
                        for item in descr_obj:
                            descrname += item.get_text(strip=True)
                        #print(descrname)
                        sample_string_bytes = descrname.encode("utf-8")  
                        base64_bytes = base64.b64encode(sample_string_bytes)
                        base64_string = base64_bytes.decode("ascii")

                        print('==='*30)
                        parsed = [
                            id,
                            name,
                            buildername,
                            subname,
                            jkname,
                            metroname,
                            addrname,
                            pricename,
                            m2pricename,
                            base64_string,
                            link
                        ]
                        writer.writerow(parsed)
                        n += 1
                    except:
                        print("Error while row writing.. skip")
        except:
                print("Error while writing csv file")

    return n


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
    for page in range(1, pages + 1):
        link = url + f'&page={str(page)}'
        try:
            browser.get(link)
            time.sleep(1)
            html = browser.page_source
            parsed_page = get_content_page(html)
            #print(parsed_page)
            print('==='*20)
            print(f'Парсинг страницы {page} завершен. Собрано {parsed_page} позиций')
        except Exception as ex:
            print(f'Не предвиденная ошибка: {ex}')
            browser.close()
            browser.quit()
    print('Сбор данных завершен.')
    return True


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
    # sys.exit()
    # headers = ['name', 'city','area','link','price']    
    # with open('dataset.csv', mode='w', encoding='utf-8', errors='ignore') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=",")
    #     writer.writerow(headers)
    #     csvfile.close()
    #url = input('Введите ссылку на раздел, с заранее выбранными характеристиками (ценовой диапазон и тд):\n')
    url = 'https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=1room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1'
    print('Запуск парсера...')
    save_exel(parser(url))