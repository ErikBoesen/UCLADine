from app import app, db, celery
from app.models import Location, Meal, Item, Nutrition

from celery.schedules import crontab

import os
import requests
import datetime
from bs4 import BeautifulSoup

DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H %a'


def scrape_item(item_element):
    pass


def scrape():
    hall_slugs = ['DeNeve']
    for hall_slug in hall_slugs:
        date = datetime.datetime.now().strftime(DATE_FMT)
        html = requests.get(f'https://menu.dining.ucla.edu/Menus/{hall_slug}/{date}').text
        soup = BeautifulSoup(html, 'html.parser').find('div', {'id': 'main-content'})
        cols = soup.find_all('div', {'class': 'menu-block'})
        for col in cols:
            meal_name = col.find('h3', {'class': 'col-header'})
            menu_list = col.find('ul', {'class': 'sect-list'})
            sects = col.find_all('li', {'class': 'sect-item'})
            for sect in sects:
                course_name = sect.find_all(text=True, recursive=False)[0].strip()
                item_list = sect.find('ul', {'class': 'item-list'})
                item_elements = item_list.find_all('li', {'class': 'menu-item'})
                for item_element in item_elements:
                    scrape_item(item_element)



@celery.task
def scrape_task(fasttrack_only=False):
    scrape()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, scrape.s(), name='Website scrape')
