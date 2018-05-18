#!/usr/bin/env python

from myapp.models import *
from bs4 import BeautifulSoup
import datetime

def save_to_database(path):
    '''Save a standardized XML file to database'''
    with open(path, 'r', encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    branch = Branch()
    branch.title = soup.title.text
    branch.intro = soup.intro.text
    branch.chairman = soup.chairman.text
    branch.source = soup.source.text

    raw_date = soup.pub_date.text
    y, m, d = [int(t) for t in raw_date.split('.')]

    branch.pub_date = datetime.date(y, m, d)
    branch.save()

    flag = 0
    for article_soup in soup.findAll('article'):
        flag += 1
        article = Article()
        article.num = flag
        article.branch = branch

        children = article_soup.children
        for child in children:
            article.article_text += str(child).replace('\n', '') # contain tags like '<p>'
        article.save()

def wipe_all_branches():
    for b in Branch.objects.all():
        b.delete()

def check_xml(path, total): # total 法条总数
    '''Check if the XML file is standardized'''
    with open(path, 'r', encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    article_soup = soup.findAll('article')
    for i, j in zip(list(range(1, total+1)), article_soup):
        print(i, '\t', j.span.text)














