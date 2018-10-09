from bs4 import BeautifulSoup
import datetime
from tinydb import TinyDB, Query, where
import urllib3
import requests
import random
import os
from PIL import Image
from tqdm import tqdm


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    get_db() 


def get_db():
    # create a database for the image information
    global db
    db = TinyDB('./db.json')

    # get a list of all the cities in the US craigslist covers
    address_dict = get_cities()
    cities = list(address_dict.items())

    # for each city find the free postings, extract the 300x300 image
    # and write the image information to the database
    for i, city in enumerate(cities):
        print (str(i) + ' ' + city[0])
        url = city[1] + 'd/free-stuff/search/zip'
        global city_name
        city_name = city[0].replace(' ', '')
        city_name = city_name.replace('/', '')

        while url:
            soup = soup_process(url)
            nextlink = soup.find("link", rel="next")

            url = False
            if (nextlink):
                url = nextlink['href']


def soup_process(url):
    soup = make_soup(url)
    results = soup.find_all("li", class_="result-row")
    for result in tqdm(results):
        try:
            img_url = clean_pic(result.a['data-ids'])

            if not db.search(where(img_url)):

                img_name = img_url.split('/')[-1]
                time_stamp = result.p.time['datetime']
                descr = result.p.a.string.strip()

                img_info = {img_url: [time_stamp, city_name, descr]}

                out_dir = os.path.join('.','out', city_name)
                if not os.path.isdir(out_dir):
                    os.makedirs(out_dir)

                out_path = os.path.join(out_dir, img_name)
                img = Image.open(requests.get(img_url, stream = True).raw)
                img.save(out_path)

                # print (descr)
                db.insert(img_info)

        except (AttributeError, KeyError, OSError) as ex:
            # print (ex)
            pass

    return soup


def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data, 'lxml')


def get_cities():
    url = 'https://www.craigslist.org/about/sites'
    soup = make_soup(url)
    results = soup.select_one('h1 + div').find_all('a')

    address_dict = {}
    for result in results:
        if result.text:
            address = {result.contents[0]: result['href']}
            address_dict.update(address)

    return address_dict


def clean_pic(ids):
    idlist = ids.split(",")
    first = idlist[0]
    code = first.replace("1:", "")
    # return "https://images.craigslist.org/%s_1200x900.jpg" % code
    return "https://images.craigslist.org/%s_300x300.jpg" % code


main()
