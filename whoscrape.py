from __future__ import print_function
from datetime import date, datetime, timedelta
from sys import argv
import mysql.connector
import urllib.request
import json
import config

class WhoScrape:
  def __init__(self):
    self.setConfig()
    self.run()

  def setConfig(self):
    self.username = config.username
    self.password = config.password
    self.format   = config.format
    self.database = config.database
    self.mock     = config.mock

  def run(self):
    f = open('domains','r')
    for line in f:
      self.domain = line.strip()
      print("Checking domain: " + self.domain)
      data = self.getWhoIs()
      if(data):
        print('Saving data...')
        self.sqlInsert(data)
      else:
        print('Data not saved.')
        print(data)

  def getWhoIs(self):
    if(self.mock):
      data = {
        "domain": "testing.com",
        "email": "test@example.com",
        "registrar": "Enom, Inc."
      }
    else:
      data = False
      url  = 'http://www.whoisxmlapi.com/whoisserver/WhoisService?domainName=' + self.domain + '&username=' + self.username + '&password=' + self.password + '&outputFormat=' + self.format
      connect = urllib.request.urlopen(url)
      result  = json.loads(connect.readall().decode('utf8'))
      connect.close()
       
      if ('WhoisRecord' in result):
        data = {
          "domain": self.domain,
          "email": result['WhoisRecord']['registrant']['email'],
          "registrar": result['WhoisRecord']['registrarName']
        }
      else:
        print(result)
    return data

  def sqlInsert(self, data):
    table = self.database['db_table']
    cnx = mysql.connector.connect(user=self.database['db_user'], database=self.database['db_name'])
    cursor = cnx.cursor()

    add_domain = ("INSERT INTO " + table + " "
                   "(domain, email, registrar) "
                   "VALUES (%s, %s, %s)")

    data_domain = (data['domain'], data['email'], data['registrar'])

    cursor.execute(add_domain, data_domain)

    cnx.commit()
    cursor.close()
    cnx.close()

WhoScrape()
