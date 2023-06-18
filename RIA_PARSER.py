import time
import requests
from bs4 import BeautifulSoup
import datetime
import timeit
import pytz

def __timestamp_to_msk_str__(timestamp):
    utc_dt = datetime.datetime.utcfromtimestamp(timestamp)
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    msk_dt = utc_dt.astimezone(pytz.timezone("Europe/Moscow"))
    msk_str = msk_dt.strftime("%d-%m-%Y %H:%M:%S")
    return msk_str

class Article:
    def __init__(self, title, link, timestamp):
        self.title = title
        self.link = link
        self.timestamp = timestamp
        # переводим timestamp в мск дату и время
        self.date = __timestamp_to_msk_str__(timestamp)

    def __str__(self):
        return f"{self.title};{self.link};{self.date};{self.timestamp}"

class Ria_Parser:
    def __init__(self):
        self.ria_ru = "https://ria.ru"
        self.ria_lenta = "https://ria.ru/lenta"
        self.ria_archive = "https://ria.ru/services/archive/widget/more.html?id=0"

    def __get_article_date_timestamp__(self, article_date, article_time):
        # получаем год, месяц, день
        year = int(article_date[0:4])
        month = int(article_date[4:6])
        day = int(article_date[6:])
        # получаем часы, минуты
        article_time = article_time.split(":")
        hours = int(article_time[0])
        minutes = int(article_time[1])
        # получаем timestamp
        t = datetime.datetime(year, month, day, hours, minutes)
        ts = time.mktime(t.timetuple())
        return ts

    def parse_articles(self, count):
        articles = []
        counter = 0
        data_next_link = self.ria_archive
        while (True):
            # получаем следующие 20 новостей
            next_twenty_articles_html = requests.get(data_next_link).text
            soup = BeautifulSoup(next_twenty_articles_html, 'html.parser')
            lenta_items = soup.find_all("div", class_="lenta__item")

            for lenta_item in lenta_items:
                # получаем ссылку
                href = lenta_item.find(class_="lenta__item-size").get("href")
                link = self.ria_lenta + href
                # получаем заголовок
                title = lenta_item.find(class_="lenta__item-text").text
                # получаем время и дату выхода новости в timestamp
                article_date = href.strip("/").split("/")[0]
                article_time = lenta_item.find(class_="lenta__item-date").text
                ts = self.__get_article_date_timestamp__(article_date, article_time)
                # добавляем статью в класс
                articles.append(Article(title, link, ts))
                counter = counter + 1
                print(counter)
                if (counter == count): return articles

            # получаем ссылку на api кнопки "еще"
            # которая выдает следующие 20 статей
            last_lenta_item = lenta_items[-1]
            data_next_link = self.ria_ru + last_lenta_item.get("data-next")

def measure_time(func):
    start = timeit.default_timer()
    func()
    end = timeit.default_timer()
    print(f"Время выполнения: {end - start}s")

def write_articles_to_csv(articles):
    with open("articles.csv", "w", encoding='UTF-8') as f:
        f.write("Title;Link;Date;Timestamp" + "\n")
        for article in articles:
            f.write(article.__str__() + "\n")

def __main__():
    parser = Ria_Parser()
    parse_count = 1000
    articles = parser.parse_articles(parse_count)
    write_articles_to_csv(articles)

# функция для измерения времени парсинга
# measure_time(__main__)

__main__()