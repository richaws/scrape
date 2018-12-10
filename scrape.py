#!/usr/bin/env python3

import threading
from datetime import datetime
from datetime import timedelta
import requests
import mysql.connector
from mysql.connector import errorcode
import json
import base64
from bs4 import BeautifulSoup

# Lists
titlelist = []
datelist = []
hoodlist = []

# URL
page = requests.get('https://newyork.craigslist.org/search/sad?query=linux')

# Create a BeautifulSoup object
soup = BeautifulSoup(page.text, 'html.parser')

# Extract tags
titles = soup.findAll('a', {'class': 'result-title'})
dates = soup.findAll('time', {'class': 'result-date'})
hoods = soup.findAll('nearby', {'class': 'result-meta'})

# Extracting text from the the <a> tags, i.e. class titles.
for title in titles:
    titlelist.append(title.text)

for date in dates:
    datelist.append(date.text)

for hood in hoods:
    hoodlist.append(hood.text)

# DB stuff
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123456",
  auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor()

def scrape():

    try:
        threading.Timer(60.0, scrape).start()  # called every minute

        for a, b in zip(datelist, titlelist):
            val = (a,b)
            mydate = datetime.now()
            mycursor.execute("create database if not exists cl;")
            mycursor.execute("create table if not exists cl.jobs ( id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, date VARCHAR(30) NOT NULL, title VARCHAR(100) NOT NULL UNIQUE, reg_date TIMESTAMP );")
            sql = "INSERT INTO cl.jobs (date, title) VALUES (%s, %s)"
            mycursor.execute(sql,val)
            mydb.commit()
            print("%s Updating..." %mydate)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            print("%s Nothing new. Skipping..." %mydate)
scrape()