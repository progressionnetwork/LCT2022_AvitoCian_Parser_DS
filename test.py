# -*- coding: utf-8 -*-

import base64
import sys
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from pymystem3 import Mystem
from string import punctuation
from slugify import slugify # pip install python-slugify
from rutermextract import TermExtractor
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=Warning)

# update nltk data
nltk.download('punkt')
nltk.download('stopwords')

# create lemmatizer and stopwords list
mystem = Mystem() 
russian_stopwords = stopwords.words("russian")

# categorization of metro stations
cat_stations = {'Новокосино': 0, 'Новогиреево': 1, 'Перово': 2, 'Шоссе Энтузиастов': 231, 'Авиамоторная': 288, 'Площадь Ильича': 5, 'Марксистская': 6, 'Третьяковская': 43, 'Ховрино': 8, 'Беломорская': 9, 'Речной вокзал': 10, 'Водный стадион': 11, 'Войковская': 12, 'Сокол': 13, 'Аэропорт': 14, 'Динамо': 15, 'Белорусская': 302, 'Маяковская': 17, 'Тверская': 18, 'Театральная': 19, 'Новокузнецкая': 20, 'Павелецкая': 170, 'Автозаводская': 237, 'Технопарк': 23, 'Коломенская': 24, 'Каширская': 200, 'Кантемировская': 26, 'Царицыно': 338, 'Орехово': 28, 'Домодедовская': 29, 'Красногвардейская': 30, 'Алма-Атинская': 31, 'Медведково': 32, 'Бабушкинская': 33, 'Свиблово': 34, 'Ботанический сад': 224, 'ВДНХ': 36, 'Алексеевская': 37, 'Рижская': 327, 'Проспект Мира': 166, 'Сухаревская': 40, 'Тургеневская': 41, 'Китай-город': 154, 'Октябрьская': 172, 'Шаболовская': 45, 'Ленинский проспект': 46, 'Академическая': 47, 'Профсоюзная': 48, 'Новые Черемушки': 49, 'Калужская': 50, 'Беляево': 51, 'Коньково': 52, 'Теплый Стан': 53, 'Ясенево': 54, 'Новоясеневская': 55, 
'Бульвар Рокоссовского': 227, 'Черкизовская': 57, 'Преображенская площадь': 58, 'Сокольники': 59, 'Красносельская': 60, 'Комсомольская': 167, 'Красные ворота': 62, 'Чистые пруды': 63, 'Лубянка': 64, 'Охотный ряд': 65, 'Библиотека им.Ленина': 66, 'Кропоткинская': 67, 'Парк культуры': 173, 'Фрунзенская': 69, 'Спортивная': 70, 'Воробьевы горы': 71, 'Университет': 72, 'Проспект Вернадского': 273, 'Юго-Западная': 74, 'Тропарево': 75, 'Румянцево': 76, 'Саларьево': 77, 'Филатов луг': 78, 'Прокшино ': 79, 'Ольховая ': 80, 'Коммунарка': 81, 'Щелковская': 82, 'Первомайская': 83, 'Измайловская': 84, 
'Партизанская': 85, 'Семеновская': 86, 'Электрозаводская': 287, 'Бауманская': 88, 'Площадь Революции': 89, 'Курская': 329, 'Арбатская': 113, 'Смоленская': 112, 'Киевская': 174, 'Парк Победы': 211, 'Славянский бульвар': 313, 'Кунцевская': 306, 'Молодежная': 97, 'Крылатское': 98, 'Строгино': 99, 'Мякинино': 100, 'Волоколамская': 320, 'Митино': 102, 'Пятницкое шоссе': 103, 'Пионерская': 105, 'Филевский парк': 106, 'Багратионовская': 107, 'Фили': 
305, 'Кутузовская': 243, 'Студенческая': 110, 'Александровский сад': 114, 'Выставочная': 115, 'Международная': 116, 'Алтуфьево': 117, 'Бибирево': 118, 'Отрадное': 119, 'Владыкино': 223, 'Петровско-Разумовская': 180, 'Тимирязевская': 300, 'Дмитровская': 326, 'Савёловская': 301, 'Менделеевская': 125, 'Цветной бульвар': 126, 'Чеховская': 127, 'Боровицкая': 128, 'Полянка': 129, 'Серпуховская': 130, 'Тульская': 131, 'Нагатинская': 132, 'Нагорная': 
133, 'Нахимовский проспект': 134, 'Севастопольская': 135, 'Чертановская': 136, 'Южная': 137, 'Пражская': 138, 'Улица Академика Янгеля': 139, 'Аннино': 140, 'Бульвар Дмитрия Донского': 141, 'Планерная': 142, 'Сходненская': 143, 'Тушинская': 321, 'Спартак': 145, 'Щукинская': 146, 'Октябрьское поле': 147, 'Полежаевская': 148, 'Беговая': 303, 'Улица 1905 года': 150, 'Баррикадная': 151, 'Пушкинская': 152, 'Кузнецкий мост': 153, 'Таганская': 169, 'Пролетарская': 156, 'Волгоградский проспект': 157, 'Текстильщики': 333, 'Кузьминки': 159, 'Рязанский проспект': 160, 'Выхино': 161, 'Лермонтовский проспект': 162, 'Жулебино': 163, 'Котельники': 164, 'Новослободская': 165, 'Добрынинская': 171, 'Краснопресненская': 175, 'Селигерская': 177, 'Верхние Лихоборы': 178, 'Окружная': 299, 'Фонвизинская': 181, 'Бутырская ': 182, 'Марьина Роща': 183, 'Достоевская': 184, 'Трубная': 185, 'Сретенский бульвар': 186, 'Чкаловская': 187, 'Римская': 188, 'Крестьянская застава': 189, 'Дубровка': 236, 'Кожуховская': 191, 'Печатники': 192, 'Волжская': 193, 'Люблино': 334, 'Братиславская': 195, 'Марьино': 196, 'Борисово': 197, 'Шипиловская': 198, 'Зябликово': 199, 'Варшавская': 201, 'Каховская': 277, 'Бунинская аллея': 203, 'Улица Горчакова': 204, 'Бульвар Адмирала Ушакова': 205, 'Улица Скобелевская': 206, 'Улица Старокачаловская': 207, 'Лесопарковая': 208, 'Битцевский Парк': 209, 'Деловой центр': 263, 'Минская': 212, 'Ломоносовский проспект': 213, 'Раменки': 214, 'Мичуринский проспект': 272, 'Озёрная': 216, 'Говорово ': 217, 'Солнцево': 218, 'Боровское шоссе': 219, 'Новопеределкино': 220, 'Рассказовка': 221, 'Ростокино': 225, 'Белокаменная': 226, 
'Локомотив': 228, 'Измайлово': 229, 'Соколиная Гора': 230, 'Андроновка': 232, 'Нижегородская': 285, 'Новохохловская': 332, 'Угрешская': 235, 'ЗИЛ': 238, 'Верхние Котлы': 239, 'Крымская': 240, 'Площадь Гагарина': 241, 'Лужники': 242, 'Шелепиха': 262, 'Хорошево': 246, 'Зорге': 247, 'Панфиловская': 248, 'Стрешнево': 323, 'Балтийская': 250, 'Коптево': 251, 'Лихоборы': 252, 'Улица Милашенкова': 254, 'Телецентр': 255, 'Улица Академика Королёва': 256, 'Выставочный центр': 257, 'Улица Сергея Эйзенштейна': 258, 'Петровский парк': 259, 'ЦСКА': 260, 'Хорошевская': 261, 'Мнёвники': 266, 'Народное Ополчение': 267, 'Терехово': 268, 'Давыдково': 270, 'Аминьевская': 271, 'Новаторская': 274, 'Воронцовская': 275, 'Зюзино': 276, 'Косино': 278, 'Улица Дмитриевского ': 279, 'Лухмановская': 280, 'Некрасовка': 281, 'Юго-Восточная': 282, 'Окская': 283, 'Стахановская': 284, 'Лефортово': 286, 'Лобня': 289, 
'Шереметьевская': 290, 'Хлебниково': 291, 'Водники': 292, 'Долгопрудная': 293, 'Новодачная': 294, 'Марк': 295, 'Лианозово': 296, 'Бескудниково': 297, 'Дегунино': 298, 'Тестовская': 304, 'Рабочий Посёлок': 307, 'Сетунь': 308, 'Немчиновка': 309, 'Сколково': 310, 'Баковка': 311, 'Одинцово': 312, 'Нахабино': 314, 'Аникеевка': 315, 'Опалиха': 316, 'Красногорская': 317, 'Павшино': 318, 'Пенягино': 319, 'Покровское-Стрешнево': 322, 'Красный Балтиец': 324, 'Гражданская': 325, 'Каланчёвская': 328, 'Москва Товарная': 330, 'Калитники': 331, 'Депо': 335, 'Перерва': 336, 'Москворечье': 337, 'Покровское': 339, 'Красный строитель': 340, 'Битца': 341, 'Бутово': 342, 'Щербинка': 343, 'Остафьево': 344, 'Силикатная': 345, 'Подольск': 346, 'Трикотажная': 
347, 'Курьяново': 348}

# distance coefficient for stations
coef_stations = [
    {'name': 'Новокосино', 'distance': 15.234511977471307, 'dist_coef': 1},
    {'name': 'Новогиреево', 'distance': 12.107314804837477, 'dist_coef': 1},
    {'name': 'Перово', 'distance': 10.210325154392718, 'dist_coef': 1},
    {'name': 'Шоссе Энтузиастов', 'distance': 8.182955258572829, 'dist_coef': 1},
    {'name': 'Авиамоторная', 'distance': 6.02919105681004, 'dist_coef': 1},
    {'name': 'Площадь Ильича', 'distance': 3.801557658710615, 'dist_coef': 1},
    {'name': 'Марксистская', 'distance': 2.6232324661304594, 'dist_coef': 1},
    {'name': 'Третьяковская', 'distance': 1.4472556901365028, 'dist_coef': 2},
    {'name': 'Ховрино', 'distance': 16.10572005040964, 'dist_coef': 1},
    {'name': 'Беломорская', 'distance': 15.331295740467448, 'dist_coef': 1},
    {'name': 'Речной вокзал', 'distance': 14.354224063254168, 'dist_coef': 1},
    {'name': 'Водный стадион', 'distance': 12.63059923460821, 'dist_coef': 1},
    {'name': 'Войковская', 'distance': 10.581229278004917, 'dist_coef': 1},
    {'name': 'Сокол', 'distance': 8.77583835733938, 'dist_coef': 1},
    {'name': 'Аэропорт', 'distance': 7.685564059514192, 'dist_coef': 1},
    {'name': 'Динамо', 'distance': 5.606983738543773, 'dist_coef': 1},
    {'name': 'Белорусская', 'distance': 3.587688857695084, 'dist_coef': 1},
    {'name': 'Маяковская', 'distance': 2.366941906621731, 'dist_coef': 1},
    {'name': 'Тверская', 'distance': 1.675109436525028, 'dist_coef': 2},
    {'name': 'Театральная', 'distance': 0.5950894498802183, 'dist_coef': 3},
    {'name': 'Новокузнецкая', 'distance': 1.3699959671399538, 'dist_coef': 2},
    {'name': 'Павелецкая', 'distance': 2.8953788186985077, 'dist_coef': 1},
    {'name': 'Автозаводская', 'distance': 5.7092713141638445, 'dist_coef': 1},
    {'name': 'Технопарк', 'distance': 7.076176291024265, 'dist_coef': 1},
    {'name': 'Коломенская', 'distance': 8.906967297759499, 'dist_coef': 1},
    {'name': 'Каширская', 'distance': 11.05530614581946, 'dist_coef': 1},
    {'name': 'Кантемировская', 'distance': 13.277232815067784, 'dist_coef': 1},
    {'name': 'Царицыно', 'distance': 15.085386502216402, 'dist_coef': 1},
    {'name': 'Орехово', 'distance': 16.370892047922183, 'dist_coef': 1},
    {'name': 'Домодедовская', 'distance': 17.078049894975376, 'dist_coef': 1},
    {'name': 'Красногвардейская', 'distance': 17.31186104133182, 'dist_coef': 1},
    {'name': 'Алма-Атинская', 'distance': 16.162381021757533, 'dist_coef': 1},
    {'name': 'Медведково', 'distance': 15.145932181428922, 'dist_coef': 1},
    {'name': 'Бабушкинская', 'distance': 13.26911745649783, 'dist_coef': 1},
    {'name': 'Свиблово', 'distance': 11.49204742270025, 'dist_coef': 1},
    {'name': 'Ботанический сад', 'distance': 10.148666388538667, 'dist_coef': 1},
    {'name': 'ВДНХ', 'distance': 7.419477401991236, 'dist_coef': 1},
    {'name': 'Алексеевская', 'distance': 6.101008057790635, 'dist_coef': 1},
    {'name': 'Рижская', 'distance': 4.400357007728358, 'dist_coef': 1},
    {'name': 'Проспект Мира', 'distance': 3.203106927929137, 'dist_coef': 1},
    {'name': 'Сухаревская', 'distance': 2.1814500768693255, 'dist_coef': 1},
    {'name': 'Тургеневская', 'distance': 1.610556893516592, 'dist_coef': 2},
    {'name': 'Китай-город', 'distance': 0.7007149011162476, 'dist_coef': 3},
    {'name': 'Третьяковская', 'distance': 1.4837776428936063, 'dist_coef': 2},
    {'name': 'Октябрьская', 'distance': 2.5674384207796614, 'dist_coef': 1},
    {'name': 'Шаболовская', 'distance': 3.981494587565494, 'dist_coef': 1},
    {'name': 'Ленинский проспект', 'distance': 5.703372666735644, 'dist_coef': 1},
    {'name': 'Академическая', 'distance': 8.024572111580875, 'dist_coef': 1},
    {'name': 'Профсоюзная', 'distance': 9.232360918228725, 'dist_coef': 1},
    {'name': 'Новые Черемушки', 'distance': 10.210200041112154, 'dist_coef': 1},
    {'name': 'Калужская', 'distance': 11.941625831005572, 'dist_coef': 1},
    {'name': 'Беляево', 'distance': 13.756732132486325, 'dist_coef': 1},
    {'name': 'Коньково', 'distance': 14.999093714834883, 'dist_coef': 1},
    {'name': 'Теплый Стан', 'distance': 16.674826052587573, 'dist_coef': 1},
    {'name': 'Ясенево', 'distance': 17.320802733312078, 'dist_coef': 1},
    {'name': 'Новоясеневская', 'distance': 17.42627435633914, 'dist_coef': 1},
    {'name': 'Бульвар Рокоссовского', 'distance': 9.715640112362802, 'dist_coef': 1},
    {'name': 'Черкизовская', 'distance': 9.460626411010374, 'dist_coef': 1},
    {'name': 'Преображенская площадь', 'distance': 7.466390871867178, 'dist_coef': 1},
    {'name': 'Сокольники', 'distance': 5.388808326129491, 'dist_coef': 1},
    {'name': 'Красносельская', 'distance': 4.046977858871343, 'dist_coef': 1},
    {'name': 'Комсомольская', 'distance': 3.0710286392100206, 'dist_coef': 1},
    {'name': 'Красные ворота', 'distance': 2.316567677763776, 'dist_coef': 1},
    {'name': 'Чистые пруды', 'distance': 1.6390960709419067, 'dist_coef': 2},
    {'name': 'Лубянка', 'distance': 0.7219658771834963, 'dist_coef': 3},
    {'name': 'Охотный ряд', 'distance': 0.5370809115632386, 'dist_coef': 3},
    {'name': 'Библиотека им.Ленина', 'distance': 0.7018725870328383, 'dist_coef': 3},
    {'name': 'Кропоткинская', 'distance': 1.4245342115165815, 'dist_coef': 2},
    {'name': 'Парк культуры', 'distance': 2.558155400787515, 'dist_coef': 1},
    {'name': 'Фрунзенская', 'distance': 3.8963680445190354, 'dist_coef': 1},
    {'name': 'Спортивная', 'distance': 5.093824184972893, 'dist_coef': 1},
    {'name': 'Воробьевы горы', 'distance': 6.3788455520129554, 'dist_coef': 1},
    {'name': 'Университет', 'distance': 8.650018411634818, 'dist_coef': 1},
    {'name': 'Проспект Вернадского', 'distance': 11.280996468123764, 'dist_coef': 1},
    {'name': 'Юго-Западная', 'distance': 13.299870474931923, 'dist_coef': 1},
    {'name': 'Тропарево', 'distance': 15.19767118441201, 'dist_coef': 1},
    {'name': 'Румянцево', 'distance': 17.519887227958215, 'dist_coef': 1},
    {'name': 'Саларьево', 'distance': 19.120045420261874, 'dist_coef': 1},
    {'name': 'Филатов луг', 'distance': 21.760067483382137, 'dist_coef': 1},
    {'name': 'Прокшино ', 'distance': 22.22396563787842, 'dist_coef': 1},
    {'name': 'Ольховая ', 'distance': 22.921550787465996, 'dist_coef': 1},
    {'name': 'Коммунарка', 'distance': 23.61061761418826, 'dist_coef': 1},
    {'name': 'Щелковская', 'distance': 12.714162121347673, 'dist_coef': 1},
    {'name': 'Первомайская', 'distance': 12.024671074775942, 'dist_coef': 1},
    {'name': 'Измайловская', 'distance': 10.621006433674026, 'dist_coef': 1},
    {'name': 'Партизанская', 'distance': 8.86306048149796, 'dist_coef': 1},
    {'name': 'Семеновская', 'distance': 6.947999730639287, 'dist_coef': 1},
    {'name': 'Электрозаводская', 'distance': 6.1283617721676045, 'dist_coef': 1},
    {'name': 'Бауманская', 'distance': 4.168455678115876, 'dist_coef': 1},
    {'name': 'Площадь Революции', 'distance': 0.3316787299620382, 'dist_coef': 3},
    {'name': 'Курская', 'distance': 2.4271841068226023, 'dist_coef': 1},
    {'name': 'Арбатская', 'distance': 1.1202194609486646, 'dist_coef': 2},
    {'name': 'Смоленская', 'distance': 2.436870186760663, 'dist_coef': 1},
    {'name': 'Киевская', 'distance': 3.7650145982065535, 'dist_coef': 1},
    {'name': 'Парк Победы', 'distance': 6.835982610758744, 'dist_coef': 1},
    {'name': 'Славянский бульвар', 'distance': 9.785255836555786, 'dist_coef': 1},
    {'name': 'Кунцевская', 'distance': 11.234936774832752, 'dist_coef': 1},
    {'name': 'Молодежная', 'distance': 12.942615455285821, 'dist_coef': 1},
    {'name': 'Крылатское', 'distance': 13.338539329080938, 'dist_coef': 1},
    {'name': 'Строгино', 'distance': 14.771716355589405, 'dist_coef': 1},
    {'name': 'Мякинино', 'distance': 16.65918870269968, 'dist_coef': 1},
    {'name': 'Волоколамская', 'distance': 17.45357107541704, 'dist_coef': 1},
    {'name': 'Митино', 'distance': 19.221152664953777, 'dist_coef': 1},
    {'name': 'Пятницкое шоссе', 'distance': 20.100906041762155, 'dist_coef': 1},
    {'name': 'Кунцевская', 'distance': 11.217163653850834, 'dist_coef': 1},
    {'name': 'Пионерская', 'distance': 9.87057567614121, 'dist_coef': 1},
    {'name': 'Филевский парк', 'distance': 8.737514319522042, 'dist_coef': 1},
    {'name': 'Багратионовская', 'distance': 7.8550402773495644, 'dist_coef': 1},
    {'name': 'Фили', 'distance': 6.753114503764743, 'dist_coef': 1},
    {'name': 'Кутузовская', 'distance': 5.6484098746386735, 'dist_coef': 1},
    {'name': 'Студенческая', 'distance': 4.85390093387894, 'dist_coef': 1},
    {'name': 'Киевская', 'distance': 3.68649244113283, 'dist_coef': 1},
    {'name': 'Смоленская', 'distance': 2.498292047251098, 'dist_coef': 1},
    {'name': 'Арбатская', 'distance': 1.243270374292932, 'dist_coef': 2},
    {'name': 'Александровский сад', 'distance': 0.7961567767872111, 'dist_coef': 3},
    {'name': 'Выставочная', 'distance': 4.932455387924514, 'dist_coef': 1},
    {'name': 'Международная', 'distance': 5.536248241844296, 'dist_coef': 1},
    {'name': 'Алтуфьево', 'distance': 16.295022166933684, 'dist_coef': 1},
    {'name': 'Бибирево', 'distance': 14.507738674387616, 'dist_coef': 1},
    {'name': 'Отрадное', 'distance': 12.324987740664115, 'dist_coef': 1},
    {'name': 'Владыкино', 'distance': 10.674329075252311, 'dist_coef': 1},
    {'name': 'Петровско-Разумовская', 'distance': 9.634778186437371, 'dist_coef': 1},
    {'name': 'Тимирязевская', 'distance': 7.779060025152016, 'dist_coef': 1},
    {'name': 'Дмитровская', 'distance': 6.516158651156901, 'dist_coef': 1},
    {'name': 'Савёловская', 'distance': 4.953978012732333, 'dist_coef': 1},
    {'name': 'Менделеевская', 'distance': 3.422827405374609, 'dist_coef': 1},
    {'name': 'Цветной бульвар', 'distance': 1.9824808305035597, 'dist_coef': 2},
    {'name': 'Чеховская', 'distance': 1.5447843030186132, 'dist_coef': 2},
    {'name': 'Боровицкая', 'distance': 0.8338641886620499, 'dist_coef': 3},
    {'name': 'Полянка', 'distance': 1.9020615241859329, 'dist_coef': 2},
    {'name': 'Серпуховская', 'distance': 3.0432983485068665, 'dist_coef': 1},
    {'name': 'Тульская', 'distance': 4.91960823565466, 'dist_coef': 1},
    {'name': 'Нагатинская', 'distance': 7.978805485303919, 'dist_coef': 1},
    {'name': 'Нагорная', 'distance': 9.020407410723019, 'dist_coef': 1},
    {'name': 'Нахимовский проспект', 'distance': 10.220898526175906, 'dist_coef': 1},
    {'name': 'Севастопольская', 'distance': 11.47924776635795, 'dist_coef': 1},
    {'name': 'Чертановская', 'distance': 12.63703982387789, 'dist_coef': 1},
    {'name': 'Южная', 'distance': 14.634673893013291, 'dist_coef': 1},
    {'name': 'Пражская', 'distance': 15.934742875480264, 'dist_coef': 1},
    {'name': 'Улица Академика Янгеля', 'distance': 17.515070957612515, 'dist_coef': 1},
    {'name': 'Аннино', 'distance': 19.00877570558335, 'dist_coef': 1},
    {'name': 'Бульвар Дмитрия Донского', 'distance': 20.833694814363067, 'dist_coef': 1},
    {'name': 'Планерная', 'distance': 16.474517144896883, 'dist_coef': 1},
    {'name': 'Сходненская', 'distance': 15.487916774080963, 'dist_coef': 1},
    {'name': 'Тушинская', 'distance': 14.004539423474409, 'dist_coef': 1},
    {'name': 'Спартак', 'distance': 13.658136067436764, 'dist_coef': 1},
    {'name': 'Щукинская', 'distance': 11.652863009632936, 'dist_coef': 1},
    {'name': 'Октябрьское поле', 'distance': 9.13964378568874, 'dist_coef': 1},
    {'name': 'Полежаевская', 'distance': 6.966034612883869, 'dist_coef': 1},
    {'name': 'Беговая', 'distance': 5.21585602315996, 'dist_coef': 1},
    {'name': 'Улица 1905 года', 'distance': 3.8545471601128756, 'dist_coef': 1},
    {'name': 'Баррикадная', 'distance': 2.6167800844588562, 'dist_coef': 1},
    {'name': 'Пушкинская', 'distance': 1.6803412888278775, 'dist_coef': 2},
    {'name': 'Кузнецкий мост', 'distance': 0.8762842314417817, 'dist_coef': 3},
    {'name': 'Китай-город', 'distance': 0.7968107371877151, 'dist_coef': 3},
    {'name': 'Таганская', 'distance': 2.580964110317802, 'dist_coef': 1},
    {'name': 'Пролетарская', 'distance': 3.787505348374011, 'dist_coef': 1},
    {'name': 'Волгоградский проспект', 'distance': 5.095727793928507, 'dist_coef': 1},
    {'name': 'Текстильщики', 'distance': 8.538411219483528, 'dist_coef': 1},
    {'name': 'Кузьминки', 'distance': 10.398720042000681, 'dist_coef': 1},
    {'name': 'Рязанский проспект', 'distance': 11.52991744088791, 'dist_coef': 1},
    {'name': 'Выхино', 'distance': 12.952742637918123, 'dist_coef': 1},
    {'name': 'Лермонтовский проспект', 'distance': 15.507190361749087, 'dist_coef': 1},
    {'name': 'Жулебино', 'distance': 16.5889740892422, 'dist_coef': 1},
    {'name': 'Котельники', 'distance': 17.28583272475181, 'dist_coef': 1},
    {'name': 'Новослободская', 'distance': 3.1260497775711262, 'dist_coef': 1},
    {'name': 'Проспект Мира', 'distance': 2.9684090306555904, 'dist_coef': 1},
    {'name': 'Комсомольская', 'distance': 3.2121940623170864, 'dist_coef': 1},
    {'name': 'Курская', 'distance': 2.552300058535552, 'dist_coef': 1},
    {'name': 'Таганская', 'distance': 2.3811503599362127, 'dist_coef': 1},
    {'name': 'Павелецкая', 'distance': 2.667148374757892, 'dist_coef': 1},
    {'name': 'Добрынинская', 'distance': 2.764125149306739, 'dist_coef': 1},
    {'name': 'Октябрьская', 'distance': 2.8054674954653582, 'dist_coef': 1},
    {'name': 'Парк культуры', 'distance': 2.716213721825328, 'dist_coef': 1},
    {'name': 'Киевская', 'distance': 3.5565653842078055, 'dist_coef': 1},
    {'name': 'Краснопресненская', 'distance': 2.8524843784826666, 'dist_coef': 1},
    {'name': 'Белорусская', 'distance': 3.3993016250081416, 'dist_coef': 1},
    {'name': 'Селигерская', 'distance': 13.121853046284215, 'dist_coef': 1},
    {'name': 'Верхние Лихоборы', 'distance': 11.898840089147987, 'dist_coef': 1},
    {'name': 'Окружная', 'distance': 11.026293771754995, 'dist_coef': 1},
    {'name': 'Петровско-Разумовская', 'distance': 9.644798931366074, 'dist_coef': 1},
    {'name': 'Фонвизинская', 'distance': 7.943302450079314, 'dist_coef': 1},
    {'name': 'Бутырская ', 'distance': 6.7172404764487945, 'dist_coef': 1},
    {'name': 'Марьина Роща', 'distance': 4.447759301272644, 'dist_coef': 1},
    {'name': 'Достоевская', 'distance': 3.1292396034981635, 'dist_coef': 1},
    {'name': 'Трубная', 'distance': 1.5441137531201707, 'dist_coef': 2},
    {'name': 'Сретенский бульвар', 'distance': 1.6393506927429167, 'dist_coef': 2},
    {'name': 'Чкаловская', 'distance': 2.3970476401329637, 'dist_coef': 1},
    {'name': 'Римская', 'distance': 3.758726811836209, 'dist_coef': 1},
    {'name': 'Крестьянская застава', 'distance': 3.658838706112107, 'dist_coef': 1},
    {'name': 'Дубровка', 'distance': 5.264912299502845, 'dist_coef': 1},
    {'name': 'Кожуховская', 'distance': 6.6572691925372585, 'dist_coef': 1},
    {'name': 'Печатники', 'distance': 9.537241467957308, 'dist_coef': 1},
    {'name': 'Волжская', 'distance': 10.920699086621385, 'dist_coef': 1},
    {'name': 'Люблино', 'distance': 12.298312499691098, 'dist_coef': 1},
    {'name': 'Братиславская', 'distance': 13.23889089129712, 'dist_coef': 1},
    {'name': 'Марьино', 'distance': 13.9520175003401, 'dist_coef': 1},
    {'name': 'Борисово', 'distance': 15.51671891255042, 'dist_coef': 1},
    {'name': 'Шипиловская', 'distance': 16.583900738820684, 'dist_coef': 1},
    {'name': 'Зябликово', 'distance': 17.59606483198314, 'dist_coef': 1},
    {'name': 'Каширская', 'distance': 11.191904249022498, 'dist_coef': 1},
    {'name': 'Варшавская', 'distance': 11.183146591532603, 'dist_coef': 1},
    {'name': 'Каховская', 'distance': 11.32939507314658, 'dist_coef': 1},
    {'name': 'Бунинская аллея', 'distance': 24.901735466507194, 'dist_coef': 1},
    {'name': 'Улица Горчакова', 'distance': 24.185865895999235, 'dist_coef': 1},
    {'name': 'Бульвар Адмирала Ушакова', 'distance': 23.72660950768864, 'dist_coef': 1},
    {'name': 'Улица Скобелевская', 'distance': 23.282516917012842, 'dist_coef': 1},
    {'name': 'Улица Старокачаловская', 'distance': 20.73087679176711, 'dist_coef': 1},
    {'name': 'Лесопарковая', 'distance': 19.342939062859326, 'dist_coef': 1},
    {'name': 'Битцевский Парк', 'distance': 17.58392334640208, 'dist_coef': 1},
    {'name': 'Деловой центр', 'distance': 5.139984755622396, 'dist_coef': 1},
    {'name': 'Парк Победы', 'distance': 6.958269124173299, 'dist_coef': 1},
    {'name': 'Минская', 'distance': 8.101427748589456, 'dist_coef': 1},
    {'name': 'Ломоносовский проспект', 'distance': 8.191470451263527, 'dist_coef': 1},
    {'name': 'Раменки', 'distance': 9.70552310586661, 'dist_coef': 1},
    {'name': 'Мичуринский проспект', 'distance': 11.18487687287519, 'dist_coef': 1},
    {'name': 'Озёрная', 'distance': 14.250840110529365, 'dist_coef': 1},
    {'name': 'Говорово ', 'distance': 16.577733155325447, 'dist_coef': 1},
    {'name': 'Солнцево', 'distance': 18.54504004514529, 'dist_coef': 1},
    {'name': 'Боровское шоссе', 'distance': 19.719584524556723, 'dist_coef': 1},
    {'name': 'Новопеределкино', 'distance': 21.076664681478626, 'dist_coef': 1},
    {'name': 'Рассказовка', 'distance': 22.566873173075987, 'dist_coef': 1},
    {'name': 'Окружная', 'distance': 11.026293771754995, 'dist_coef': 1},
    {'name': 'Владыкино', 'distance': 10.546835082187208, 'dist_coef': 1},
    {'name': 'Ботанический сад', 'distance': 10.271558863536955, 'dist_coef': 1},
    {'name': 'Ростокино', 'distance': 9.95784816416133, 'dist_coef': 1},
    {'name': 'Белокаменная', 'distance': 9.818615466591075, 'dist_coef': 1},
    {'name': 'Бульвар Рокоссовского', 'distance': 10.105762225955516, 'dist_coef': 1},
    {'name': 'Локомотив', 'distance': 9.533213377406977, 'dist_coef': 1},
    {'name': 'Измайлово', 'distance': 8.534584185369464, 'dist_coef': 1},
    {'name': 'Соколиная Гора', 'distance': 7.971378158060201, 'dist_coef': 1},
    {'name': 'Шоссе Энтузиастов', 'distance': 7.985144046627521, 'dist_coef': 1},
    {'name': 'Андроновка', 'distance': 7.230396756808545, 'dist_coef': 1},
    {'name': 'Нижегородская', 'distance': 7.121519069535849, 'dist_coef': 1},
    {'name': 'Новохохловская', 'distance': 6.813695463960126, 'dist_coef': 1},
    {'name': 'Угрешская', 'distance': 6.212781164714014, 'dist_coef': 1},
    {'name': 'Дубровка', 'distance': 5.789115763420099, 'dist_coef': 1},
    {'name': 'Автозаводская', 'distance': 5.903093185139767, 'dist_coef': 1},
    {'name': 'ЗИЛ', 'distance': 6.403129641641358, 'dist_coef': 1},
    {'name': 'Верхние Котлы', 'distance': 7.101440856845838, 'dist_coef': 1},
    {'name': 'Крымская', 'distance': 7.167798248419934, 'dist_coef': 1},
    {'name': 'Площадь Гагарина', 'distance': 5.6657989439768155, 'dist_coef': 1},
    {'name': 'Лужники', 'distance': 5.213235811891088, 'dist_coef': 1},
    {'name': 'Кутузовская', 'distance': 5.686488513261048, 'dist_coef': 1},
    {'name': 'Деловой центр', 'distance': 5.617005664950562, 'dist_coef': 1},
    {'name': 'Шелепиха', 'distance': 5.999022349425978, 'dist_coef': 1},
    {'name': 'Хорошево', 'distance': 7.590548785056045, 'dist_coef': 1},
    {'name': 'Зорге', 'distance': 8.221828075929071, 'dist_coef': 1},
    {'name': 'Панфиловская', 'distance': 9.162363046332532, 'dist_coef': 1},
    {'name': 'Стрешнево', 'distance': 10.709635562938939, 'dist_coef': 1},
    {'name': 'Балтийская', 'distance': 11.193895089478533, 'dist_coef': 1},
    {'name': 'Коптево', 'distance': 11.448661607313683, 'dist_coef': 1},
    {'name': 'Лихоборы', 'distance': 11.266436493531213, 'dist_coef': 1},
    {'name': 'Тимирязевская', 'distance': 7.720992235010433, 'dist_coef': 1},
    {'name': 'Улица Милашенкова', 'distance': 7.796804347001764, 'dist_coef': 1},
    {'name': 'Телецентр', 'distance': 7.597532449146091, 'dist_coef': 1},
    {'name': 'Улица Академика Королёва', 'distance': 7.571238507895648, 'dist_coef': 1},
    {'name': 'Выставочный центр', 'distance': 7.888556325988526, 'dist_coef': 1},
    {'name': 'Улица Сергея Эйзенштейна', 'distance': 8.525477016667073, 'dist_coef': 1},
    {'name': 'Петровский парк', 'distance': 5.76325686685824, 'dist_coef': 1},
    {'name': 'ЦСКА', 'distance': 6.496570986964598, 'dist_coef': 1},
    {'name': 'Хорошевская', 'distance': 6.823010270161862, 'dist_coef': 1},
    {'name': 'Шелепиха', 'distance': 5.987456814803092, 'dist_coef': 1},
    {'name': 'Деловой центр', 'distance': 5.139984755622396, 'dist_coef': 1},
    {'name': 'Савёловская', 'distance': 4.953978012732333, 'dist_coef': 1},
    {'name': 'Электрозаводская', 'distance': 6.1283617721676045, 'dist_coef': 1},
    {'name': 'Мнёвники', 'distance': 9.410217287477275, 'dist_coef': 1},
    {'name': 'Народное Ополчение', 'distance': 116.61524643837875, 'dist_coef': 1},
    {'name': 'Терехово', 'distance': 52.544021452088344, 'dist_coef': 1},
    {'name': 'Кунцевская', 'distance': 11.287102207645605, 'dist_coef': 1},
    {'name': 'Давыдково', 'distance': 10.684864938949424, 'dist_coef': 1},
    {'name': 'Аминьевская', 'distance': 11.678047441162358, 'dist_coef': 1},
    {'name': 'Мичуринский проспект', 'distance': 11.218577856877747, 'dist_coef': 1},
    {'name': 'Проспект Вернадского', 'distance': 11.160091434864002, 'dist_coef': 1},
    {'name': 'Новаторская', 'distance': 11.199194616638708, 'dist_coef': 1},
    {'name': 'Воронцовская', 'distance': 11.755244027764734, 'dist_coef': 1},
    {'name': 'Зюзино', 'distance': 29.536662539668054, 'dist_coef': 1},
    {'name': 'Каховская', 'distance': 11.300232512970808, 'dist_coef': 1},
    {'name': 'Косино', 'distance': 15.487158423851515, 'dist_coef': 1},
    {'name': 'Улица Дмитриевского ', 'distance': 16.901400849592616, 'dist_coef': 1},
    {'name': 'Лухмановская', 'distance': 18.22148362556155, 'dist_coef': 1},
    {'name': 'Некрасовка', 'distance': 19.938640772337198, 'dist_coef': 1},
    {'name': 'Юго-Восточная', 'distance': 13.372047441689663, 'dist_coef': 1},
    {'name': 'Окская', 'distance': 10.050135932487924, 'dist_coef': 1},
    {'name': 'Стахановская', 'distance': 9.086955081957784, 'dist_coef': 1},
    {'name': 'Нижегородская', 'distance': 7.3108764919063285, 'dist_coef': 1},
    {'name': 'Лефортово', 'distance': 5.241250972658, 'dist_coef': 1},
    {'name': 'Электрозаводская', 'distance': 6.1283617721676045, 'dist_coef': 1},
    {'name': 'Авиамоторная', 'distance': 6.02919105681004, 'dist_coef': 1},
    {'name': 'Лобня', 'distance': 34.70835376289647, 'dist_coef': 1},
    {'name': 'Шереметьевская', 'distance': 26.703819377019155, 'dist_coef': 1},
    {'name': 'Хлебниково', 'distance': 25.1923604648027, 'dist_coef': 1},
    {'name': 'Водники', 'distance': 23.23785059829951, 'dist_coef': 1},
    {'name': 'Долгопрудная', 'distance': 21.49621621941567, 'dist_coef': 1},
    {'name': 'Новодачная', 'distance': 19.85254659644372, 'dist_coef': 1},
    {'name': 'Марк', 'distance': 17.536315226552446, 'dist_coef': 1},
    {'name': 'Лианозово', 'distance': 16.513542360197636, 'dist_coef': 1},
    {'name': 'Бескудниково', 'distance': 14.718227672583843, 'dist_coef': 1},
    {'name': 'Дегунино', 'distance': 12.815578393640815, 'dist_coef': 1},
    {'name': 'Окружная', 'distance': 11.026293771754995, 'dist_coef': 1},
    {'name': 'Тимирязевская', 'distance': 7.779060025152016, 'dist_coef': 1},
    {'name': 'Савёловская', 'distance': 4.945503225388001, 'dist_coef': 1},
    {'name': 'Белорусская', 'distance': 3.3993016250081416, 'dist_coef': 1},
    {'name': 'Беговая', 'distance': 5.21585602315996, 'dist_coef': 1},
    {'name': 'Тестовская', 'distance': 5.610383862639143, 'dist_coef': 1},
    {'name': 'Фили', 'distance': 6.7609723059872495, 'dist_coef': 1},
    {'name': 'Кунцевская', 'distance': 11.294725928166446, 'dist_coef': 1},
    {'name': 'Рабочий Посёлок', 'distance': 13.216251503985829, 'dist_coef': 1},
    {'name': 'Сетунь', 'distance': 14.415964213195684, 'dist_coef': 1},
    {'name': 'Немчиновка', 'distance': 16.013897748588345, 'dist_coef': 1},
    {'name': 'Сколково', 'distance': 15.665883757441142, 'dist_coef': 1},
    {'name': 'Баковка', 'distance': 20.73294100180931, 'dist_coef': 1},
    {'name': 'Одинцово', 'distance': 23.113235985794372, 'dist_coef': 1},
    {'name': 'Славянский бульвар', 'distance': 9.804836728007613, 'dist_coef': 1},
    {'name': 'Нахабино', 'distance': 28.95055920602535, 'dist_coef': 1},
    {'name': 'Аникеевка', 'distance': 26.563315512201985, 'dist_coef': 1},
    {'name': 'Опалиха', 'distance': 24.653041929262113, 'dist_coef': 1},
    {'name': 'Красногорская', 'distance': 20.995701124022442, 'dist_coef': 1},
    {'name': 'Павшино', 'distance': 18.780217075680792, 'dist_coef': 1},
    {'name': 'Пенягино', 'distance': 17.973454964349173, 'dist_coef': 1},
    {'name': 'Волоколамская', 'distance': 17.45357107541704, 'dist_coef': 1},
    {'name': 'Тушинская', 'distance': 14.004539423474409, 'dist_coef': 1},
    {'name': 'Покровское-Стрешнево', 'distance': 11.256963934982139, 'dist_coef': 1},
    {'name': 'Стрешнево', 'distance': 10.709635562938939, 'dist_coef': 1},
    {'name': 'Красный Балтиец', 'distance': 9.068111602272072, 'dist_coef': 1},
    {'name': 'Гражданская', 'distance': 7.153124830767853, 'dist_coef': 1},
    {'name': 'Дмитровская', 'distance': 6.516158651156901, 'dist_coef': 1},
    {'name': 'Рижская', 'distance': 4.400357007728358, 'dist_coef': 1},
    {'name': 'Каланчёвская', 'distance': 3.155767217359479, 'dist_coef': 1},
    {'name': 'Курская', 'distance': 2.5132305380050664, 'dist_coef': 1},
    {'name': 'Москва Товарная', 'distance': 4.338985657085509, 'dist_coef': 1},
    {'name': 'Калитники', 'distance': 5.532423682071273, 'dist_coef': 1},
    {'name': 'Новохохловская', 'distance': 7.288904791447492, 'dist_coef': 1},
    {'name': 'Текстильщики', 'distance': 8.51401922328893, 'dist_coef': 1},
    {'name': 'Люблино', 'distance': 12.298312499691098, 'dist_coef': 1},
    {'name': 'Депо', 'distance': 11.11351036767876, 'dist_coef': 1},
    {'name': 'Перерва', 'distance': 11.940317995092412, 'dist_coef': 1},
    {'name': 'Москворечье', 'distance': 13.241318939496495, 'dist_coef': 1},
    {'name': 'Царицыно', 'distance': 15.367333061425564, 'dist_coef': 1},
    {'name': 'Покровское', 'distance': 11.256963934982139, 'dist_coef': 1},
    {'name': 'Красный строитель', 'distance': 18.287229258150614, 'dist_coef': 1},
    {'name': 'Битца', 'distance': 20.324420678277743, 'dist_coef': 1},
    {'name': 'Бутово', 'distance': 23.229830352063836, 'dist_coef': 1},
    {'name': 'Щербинка', 'distance': 27.40445276071317, 'dist_coef': 1},
    {'name': 'Остафьево', 'distance': 28.57271239221264, 'dist_coef': 1},
    {'name': 'Силикатная', 'distance': 31.809424943376417, 'dist_coef': 1},
    {'name': 'Подольск', 'distance': 36.00697460038382, 'dist_coef': 1},
    {'name': 'Трикотажная', 'distance': 16.458093275659795, 'dist_coef': 1},
    {'name': 'Курьяново', 'distance': 12.631026808196877, 'dist_coef': 1},
]

# extract distance with safe way
def extract_dist(row, value):
    try:
        return int(row[value])
    except:
        return -1

# extract category from station name
def extract_cat(station, d):
    for idx, item in enumerate(d):
        if item == station:
            return idx
    return -1

# extract coefficient from station name
def extract_coef(station, lOd):
    for dicts in lOd:
        if dicts['name'] == station:
            return round(dicts['distance'], 4)
    return 0

# decode encoded base64 descr
def base64_dec(str):
    encoded = str
    base64_bytes = encoded.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message

# clean text from unnecessary data
def clean_text(text):
    text = text.replace('*','')
    text = text.replace('⦁', '')
    text = text.replace('-', '') 
    text = text.replace('—', '') 
    text = text.replace('–', '') 
    text = text.replace('+', '') 
    text = text.replace('!', '') 
    text = text.replace('°', '') 
    text = text.replace('.', '') 
    text = text.replace('«', '').replace('»', '') 
    text = text.replace(';', '') 
    text = text.replace('\n', ' ')     
    text = text.lower()
    text = text.replace('пожалуйста, не публикуйте это объявление на других ресурсах без разрешения', '')
    text = text.replace('на звонки отвечаем 24/7', '')  
    text = text.replace('дом', '').replace('здание', '')    
    text = text.replace('квартира', '').replace('ст', '').replace('ул', '')  
    text = text.replace('район', '').replace('жизнь', '')
    text = text.replace('20332035 году', '')
    text = text.replace('скидка', '').replace('сделка', '')
    text = text.replace('символ', '')
    text = text.replace('аренда', '')
    text = text.replace('этаж', '').replace('стена', '').replace('зеркало', '').replace('зелень', '')
    text = text.replace('минуты', '').replace('минут', '').replace('время', '')
    text = text.replace('возможность', '').replace('удовольствие', '').replace('ваше внимание', '')
    text = text.replace('зоны', '').replace('зона', '').replace('стулья', '')
    return text

# lemmatize text 
def preprocess_text(text):
    tokens = mystem.lemmatize(text.lower())
    tokens = [token for token in tokens if token not in russian_stopwords\
              and token != " " \
              and token.strip() not in punctuation]
    
    text = " ".join(tokens)    
    
    return text


text = ''
data_dict = {}

# read 5k avito dataset
columns=['rooms','m2','floor','depth','area','metro_name','metro_dist','market_price',
                             'market_query','m2_price','price','link','descr']
df = pd.read_csv('dataset_5k.csv', encoding="utf-8", #header=0,
                  names=columns                    
                )

# extract descriptions
for idx, row in df.iterrows():
    message = base64_dec(row['descr'])
    #print(message)
    text += message

    # if idx > 500:
    #     break

# prepare text
term_extractor = TermExtractor()
text = clean_text(text)

# extract new features from descriptions
new_features = []
for term in term_extractor(text):
    if term.count > 3:
        feature = slugify(term.normalized, separator='_')
        print (feature, term.normalized, term.count)
        new_features.append(feature)
        #df[feature] = term.count
        #df.loc[:, feature] = [term.count]


# select unique values
x = np.array(new_features)
new_features = np.unique(x)

# build new dataframe 
ds_colmns=['rooms','m2','floor','depth','metro_name','metro_coef',
           'metro_dist','market_price','market_query','m2_price','price']
new_df = pd.DataFrame(columns=ds_colmns)

# add new features from extracted features
for col in new_features:
    new_df.insert(loc=len(ds_colmns),column=col, value=-1)

# text ectraction of stations data
#print(extract_cat('Хлебниково', cat_stations))
#print(extract_coef('Хлебниково', coef_stations))

total_rows = df.shape[0]

# fill DataFrame with data
for idx, row in df.iterrows():
    data_dict['rooms'] = row['rooms']
    data_dict['m2'] = row['m2']
    data_dict['floor'] = row['floor']
    data_dict['depth'] = row['depth']
    data_dict['metro_name'] = extract_cat(row['metro_name'], cat_stations)
    data_dict['metro_coef'] = extract_coef(row['metro_name'], coef_stations)
    data_dict['metro_dist'] = extract_dist(row, 'metro_dist')
    data_dict['market_price'] = row['market_price']
    data_dict['market_query'] = row['market_query']
    data_dict['m2_price'] = row['m2_price']
    data_dict['price'] = row['price']

    # extract description from base64
    message = base64_dec(row['descr'])
    text = clean_text(message)

    # extract and set up new features from descriptions
    for term in term_extractor(text):
        feature = slugify(term.normalized, separator='_')
        if feature in new_df.columns:
            #print('>>> set feature', feature, 'to 1.')
            new_df.loc[idx, feature] = 1

    new_df = new_df.append(data_dict, ignore_index=True)

    print('* Current row: {}/{}'.format(idx, total_rows))


    # if idx > 500:
    #     break

new_df = new_df.replace(np.nan,0)
print(new_df.head(10))
new_df.to_csv('result.csv')

print('Done. File result.csv is written!')


#########################################################################
# tests
#########################################################################

# text = clean_text(text)
# tokens = sent_tokenize(text, language="russian")
# filtered_tokens = []
# for token in tokens:
#     if token not in russian_stopwords:
#         filtered_tokens.append(token)
# print(filtered_tokens[:200])

#text = text.encode('utf-8')
# tokens = word_tokenize(text, language="russian")
# filtered_tokens = []
# for token in tokens:
#     if token not in russian_stopwords:
#         filtered_tokens.append(token)

# print(filtered_tokens[:200])

# processed_text = preprocess_text(text[:500])
# tokens = word_tokenize(processed_text, language="russian")
# print(tokens)

