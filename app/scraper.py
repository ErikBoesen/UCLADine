from app import app, db, celery
from app.models import Location, Meal, Item, Nutrition

from celery.schedules import crontab

import os
import json
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
    for seq in ('Contains ', ' Menu Option', ' Footprint'):
        name = name.replace(seq, '')
    name = name.lower().replace(' ', '_')
    return name


def scrape_nutrition(nutrition_elem):
    print('Getting nutrition facts.')
    nutrition = Nutrition()

    nutrition.serving_size = nutrition_elem.find('p', {'class': 'nfserv'}).text.replace('Serving Size ', '')
    calories_elem = nutrition_elem.find('p', {'class': 'nfcal'})
    nutrition.calories = int(calories_elem.find(text=True, recursive=False))
    fat_calories = nutrition_elem.find('span', {'class': 'nffatcal'}).text.replace('Fat Cal. ', '')
    if fat_calories != '--':
        nutrition.fat_calories = int(fat_calories)
    nutrient_elems = nutrition_elem.find_all('p', {'class': 'nfnutrient'})
    # Parse nutrition rows
    for nutrient_elem in nutrient_elems:
        tokens = nutrient_elem.text.strip().split()
        last = tokens.pop()
        # Check if there's a percent daily value at the end of the line
        pdv = None
        if last.endswith('%'):
            pdv = last.rstrip('%')
            if pdv != '--':
                pdv = int(pdv)
            else:
                pdv = 0
            last = tokens.pop()
        amount = last
        amount = amount.replace('--', '0')
        name = '_'.join(tokens).lower()
        setattr(nutrition, name, amount)
        setattr(nutrition, name + '_pdv', pdv)
    # Parse vitamins and minerals at bottom
    vm_elems = nutrition_elem.find_all('span', {'class': ('nfvitleft', 'nfvitright')})
    for vm_elem in vm_elems:
        name = vm_elem.find('span', {'class': 'nfvitname'}).text.lower().replace(' ', '_')
        pdv = vm_elem.find('span', {'class': 'nfvitpct'}).text.rstrip('%')
        if pdv != '--':
            pdv = int(pdv)
            setattr(nutrition, name + '_pdv', pdv)
    return nutrition


def scrape_item(item_elem) -> Item:
    item = Item()

    link = item_elem.find('a', {'class': 'recipelink'})
    # First try to fetch detail page.
    page = requests.get(link['href'] + '/Boxed').text
    soup = BeautifulSoup(page, 'html.parser').find('div', {'class': 'recipecontainer'})
    if soup is not None:
        item.name = soup.find('h2').text
        print('Parsing full report for ' + item.name)
        info = soup.find('div', {'class': 'productinfo'})
        description_elem = info.find('div', {'class': 'description'})
        if description_elem is not None:
            item.description = description_elem.text
        traits = info.find_all('div', {'class': 'prodwebcode'})
        for trait in traits:
            setattr(item, trait_format(trait.text), True)
        nutrition_elem = soup.find('div', {'class': 'nfbox'})
        item.nutrition = scrape_nutrition(nutrition_elem)
        ingredients = soup.find('div', {'class': 'ingred_allergen'}).find('p').find(text=True, recursive=False)
        if ingredients:
            ingredients = html.unescape(ingredients.strip())
        item.ingredients = ingredients
        image = item_elem.find('img', {'class': 'recipeimage'})
        if image is not None:
            item.image_url = 'http://menu.dining.ucla.edu' + image['src']
    else:
        item.name = link.text.strip()
        print('Parsing limited report for ' + item.name)
        description_elem = item_elem.find('div', {'class': 'item-description'})
        description = description_elem.find(text=True, recursive=False)
        if description:
            description = description.strip()
        item.description = description
        traits = description_elem.find_all('div', {'class': 'tt-prodwebcode'})
        for trait in traits:
            setattr(item, trait_format(trait.text), True)
    return item


def scrape():
    with open('res/locations.json', 'r') as f:
        locations_data = json.load(f)
    for location_slug in locations_data:
        print('Parsing location ' + location_slug)
        location_data = locations_data[location_slug]
        location = Location.query.get(location_slug)
        if location is None:
            location = Location(
                id=location_slug,
                name=location_data['name'],
                open=False,
            )
            db.session.add(location)
        date = datetime.date.today()
        date_str = date.strftime(DATE_FMT)
        print('Parsing date ' + date_str)
        html = requests.get(f'https://menu.dining.ucla.edu/Menus/{location_slug}/{date_str}').text
        soup = BeautifulSoup(html, 'html.parser').find('div', {'id': 'main-content'})
        cols = soup.find_all('div', {'class': 'menu-block'})
        for col in cols:
            meal_name = col.find('h3', {'class': 'col-header'}).text
            print('Parsing meal ' + meal_name)
            meal = Meal()
            meal.name = meal_name
            meal.date = date
            meal.location = location
            db.session.add(meal)
            menu_list = col.find('ul', {'class': 'sect-list'})
            sects = col.find_all('li', {'class': 'sect-item'})
            for sect in sects:
                course_name = sect.find_all(text=True, recursive=False)[0].strip()
                item_list = sect.find('ul', {'class': 'item-list'})
                item_elems = item_list.find_all('li', {'class': 'menu-item'})
                # TODO: designate items as addons, and figure out how to deal with conflicting items where som have different addons
                # Idea: put them all into a list and then insert them into the DB at the very end?
                for item_elem in item_elems:
                    item = scrape_item(item_elem)
                    item.course = course_name
                    db.session.add(item)
    db.session.commit()




@celery.task
def scrape_task(fasttrack_only=False):
    scrape()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, scrape.s(), name='Website scrape')
