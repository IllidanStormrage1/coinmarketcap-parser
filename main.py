import bs4
import requests
import csv
from multiprocessing import Pool
import datetime
import random


def get_html(url):
    r = requests.get(url, proxies=proxy, headers=useragent)
    return r.text

# Запись данных в csv
def write_csv(data):
    with open(name_csv, "a") as f:
        writer = csv.writer(f)
        writer.writerow((data["rank"],
                         data["name"],
                         data["price"],
                         data["pes"],
                         data["website"]))

        
# получаем все ссылки на каждую монету и набиваем ими список
def get_all_links(html):
    soup = bs4.BeautifulSoup(html, "lxml")
    tds = soup.find("table", id="currencies-all").find_all("td", class_="no-wrap currency-name")
    links = []
    for td in tds:
        a = "https://coinmarketcap.com" + str(td.find("a", class_="link-secondary").get("href"))
        links.append(a)
        
    return links


# Дергаем необходимые нам данные со страницы монеты
def get_page_data(html):
    soup = bs4.BeautifulSoup(html, "lxml")
    try:
        name = soup.find("h1", class_="details-panel-item--name").text.strip().replace("\n", " ")
    except:
        name = ""
    try:
        price = soup.find("span", id="quote_price").text.strip().replace("\n", " ")
    except:
        price = ""
    try:
        rank = soup.find("span", class_="label label-success").text
    except:
        rank = ""
    try:
        pes = soup.find_all("span", class_="h2")[-1].text.strip().replace("%", " %")
    except:
        pes = ""
    try:
        website = soup.find("ul", class_="list-unstyled details-panel-item--links").find_all("li")[1].find("a").get("href")
    except:
        website = ""

    data = {"name": name,
            "price": price,
            "rank": rank,
            "pes": pes,
            "website": website}

    return data


def main():
    global name_csv, proxy, useragent
    url = "https://coinmarketcap.com/all/views/all/"

    name_csv = str(input("Name file : ")) + ".csv"
    process = int(input("Process(CPUcores*2) : "))

    # Берем рандомный ip и useragent для избежания бана со стороны сайта
    random_proxy = random.choice(open("proxies.txt", "r").read().split("\n"))
    random_useragent = random.choice(open("useragents.txt", "r").read().split("\n"))
    proxy = {"http": "http://" + random_proxy}
    useragent = {"User-Agent": random_useragent}

    # Определяем время начала работы скрипта(основы)
    start = datetime.datetime.now()
    print("> Starting...")
    
    # Получаем список урлов монет
    links = get_all_links(get_html(url))
    print("> Parsing...")
    
    # создаем потоки, кол-во потоков равно введенному числу
    with Pool(process) as p:
        p.map(make_all, links)

    print("Parsing time: ", str(datetime.datetime.now() - start), "\nCoins:", len(links))

# Функция для потоков
def make_all(url):
    write_csv(get_page_data(get_html(url)))

    
if __name__ == "__main__":
    main()
