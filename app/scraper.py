from app import app, db, celery
from app.models import Location, Meal, Item, Nutrition

from celery.schedules import crontab

import os
import requests
from bs4 import BeautifulSoup

DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H %a'


def scrape():
    pass


@celery.task
def scrape_task(fasttrack_only=False):
    scrape()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60 * 5, scrape.s(), name='Website scrape')
