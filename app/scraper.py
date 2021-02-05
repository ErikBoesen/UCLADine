from app import app, db, celery
from app.models import Location, Meal, Item, Nutrition

from celery.schedules import crontab

import os
import requests
import datetime
from bs4 import BeautifulSoup
import html

DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H %a'


##################
# Helper methods #
##################

def trait_format(label: str) -> str:
    name = label.strip()
    for seq in ('Contains ', ' Menu Option', ' Footprint')
        name = name.replace(seq, '')
    name = name.lower().replace(' ', '_')
    return name


def scrape_nutrition(nutrition_elem):
    pass


def scrape_item(item_elem) -> Item:
    item = Item()

    link = item_elem.find('a', {'class': 'recipelink'})
    # First try to fetch detail page.
    html = requests.get(link['href'] + '/Boxed').text
    soup = BeautifulSoup(html, 'html.parser').find('div', {'class': 'recipecontainer'})
    if soup is not None:
        item.name = soup.find('h2').text
        info = soup.find('div', {'class': 'productinfo'})
        item.description = info.find('div', {'class': 'description'})
        traits = info.find_all('div', {'class': 'prodwebcode'})
        for trait in traits:
            setattr(item, trait_format(trait.text), True)
        nutrition_elem = soup.find('div', {'class': 'nfbox'})
        item.nutrition = scrape_nutrition(nutrition_elem)
        ingredients = soup.find('div', {'class': 'ingred_allergen'}).find('p').find_all(text=True, recursive=False)[0].strip()
        ingredients = html.unescape(ingredients)
        item.ingredients = ingredients
    else:
        item.name = link.text.strip()



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
                item_elems = item_list.find_all('li', {'class': 'menu-item'})
                for item_elem in item_elems:
                    item = scrape_item(item_elem)
                    item.course = course_name


@celery.task
def scrape_task(fasttrack_only=False):
    scrape()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, scrape.s(), name='Website scrape')
