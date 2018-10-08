from bs4 import BeautifulSoup
import datetime
from tinydb import TinyDB, Query
import urllib3
import requests
import random
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    #get_db()
    get_images()


def get_images():
    db = TinyDB('./db.json')
    for i in db.all():
        for key in i:
            url = key
            time_stamp, city_name, descr = i[key]

            print ('\nurl: ', url,
                '\ntime: ', time_stamp,
                '\ncity: ', city_name,
                '\ndescription: ', descr)

            out_dir = os.path.join('out', city_name.replace(' ', ''))
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)

            img_name = url.split('/')[-1]

            f = open('./%s/%s' % (out_dir, img_name),'wb')
            f.write(requests.get(url).content)
            f.close()


def get_db():
    global db
    db = TinyDB('./db.json')

    address_dict = get_cities()
    cities = list(address_dict.items())

    for city in cities:
        url = city[1] + 'd/free-stuff/search/zip'
        global city_name
        city_name = city[0].replace(' ','')
        city_name = city_name.replace('/','')

        counter = 0
        while url:
            print ("Web Page: ", url)
            soup, counter = soup_process(url, counter)
            nextlink = soup.find("link", rel="next")

            url = False
            if (nextlink):
                url = nextlink['href']

def soup_process(url, counter):
    soup = make_soup(url)
    results = soup.find_all("li", class_="result-row")
    for i, result in enumerate(results):
        try:
            img_url = clean_pic(result.a['data-ids'])
            time_stamp = result.p.time['datetime']
            descr = result.p.a.string.strip()
            counter = counter + 1
            img_info = {img_url : [time_stamp, city_name, descr]}
            db.insert(img_info)

        except (AttributeError, KeyError) as ex:
            pass

    return soup, counter


def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data,'lxml')


def get_cities():
    url = 'https://www.craigslist.org/about/sites'
    soup = make_soup(url)
    results = soup.select_one('h1 + div').find_all('a')

    address_dict = {}
    for result in results:
        if result.text:
            address = {result.contents[0]:result['href']}
            address_dict.update(address)

    return address_dict


def clean_pic(ids):
    idlist = ids.split(",")
    first = idlist[0]
    code = first.replace("1:","")
    #return "https://images.craigslist.org/%s_1200x900.jpg" % code
    return "https://images.craigslist.org/%s_300x300.jpg" % code

main()