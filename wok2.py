# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 16:21:17 2016

@author: steven
"""

'''
The Wok2 library is used to navigate and download menus from
Amherst College's NetNutrition dining menu pages.
'''
import json
import urllib.request
import urllib.parse
import re
import bs4
import requests
from collections import OrderedDict
#%%

COOKIE = 'nws43xshrrw2jz2rhr2vyjmf'# ASP.net session id

class Wok():

    url = 'https://acnutrition.amherst.edu/NetNutrition/1'
    re_getid = re.compile('[\D]+(?P<id>\d+)[\D]+')

    def __init__(self):
        self.locations = []
        # these are actually the stations! Only one real location, Val.
    def fetch_locations(self):
        r = urllib.request.Request(self.url, None, {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
            ' ASP.NET_SessionId=' + COOKIE
        })
        page = bs4.BeautifulSoup(urllib.request.urlopen(r))
        locations = page.select('.cbo_nn_sideUnitCell a')

        self.locations = []  # Clear out and repopulate the list
        for loc in locations:
            name = loc.get_text()
            lid = int(re.match(self.re_getid, loc.get('onclick')).group('id'))
            self.locations.append(Location(lid, name))

    def fetch_recursively(self):
        self.fetch_locations()
        for loc in self.locations:
            loc.fetch_stations()
            for stat in loc.stations:
                stat.fetch_menus()
                for menu in stat.menus:
                    menu.fetch_menu()
                    for item in menu.items:
                        item.fetch_nutrition()

    def get_location(self, loc):
        if not self.locations:
            raise IndexError('You have not fetched any locations')
        if isinstance(loc, int):
            for location in self.locations:
                if location.id == loc:
                    return location
            raise IndexError('Location ID not found.')
        else:
            raise TypeError('An integer Location ID must be passed.')


class Location():

    url = 'https://acnutrition.amherst.edu/NetNutrition/1/Unit/' + \
        'SelectUnitFromSideBar'
    re_getid = re.compile('[\D]+(?P<id>\d+)[\D]+')

    def __init__(self, lid, name):
        self.id = lid
        self.name = name

        self.stations = []

    def fetch_stations(self):
        postdata = urllib.parse.urlencode({'unitOid': self.id}).encode('utf8')
        r = urllib.request.Request(self.url, postdata, {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;'+\
                ' ASP.NET_SessionId=' + COOKIE
            })
        dlpage = json.loads(urllib.request.urlopen(r).read().decode('utf8'))
        for panel in dlpage['panels']:
            if panel['id'] == 'childUnitsPanel':
                page = bs4.BeautifulSoup(panel['html'])
                break

        stations = page.select('.cbo_nn_childUnitsCell a')
        if len(stations) == 0:
            self.nope = 1
        else:
            self.nope = 0

        self.stations = []  # Clear out and repopulate the list
        for stat in stations:
            name = stat.get_text()
            sid = int(re.match(self.re_getid, stat.get('onclick')).group('id'))
            self.stations.append(Station(sid, name))

        # If this location uses a default station, mark that and populate
        #   a station object.
        if not self.stations:
            for panel in dlpage['panels']:
                if panel['id'] == 'menuPanel':
                    page = bs4.BeautifulSoup(panel['html'])
                    break

            station = Station(0, 'Default', dontfetch=True)
            menus = page.select('.cbo_nn_menuCell > table')
            for menu in menus:
                datetext = menu.select('tr td')[0].get_text()
                for timeofday in menu.select('.cbo_nn_menuLink'):
                    mid = int(re.match(self.re_getid, timeofday.get('onclick')).group('id'))
                    station.menus.append(Menu(mid, datetext, timeofday.get_text()))

            self.stations.append(station)

    def get_station(self, stat):
        if not self.stations:
            raise IndexError('You have not fetched any stations')
        if isinstance(stat, int):
            for station in self.stations:
                if station.id == stat:
                    return station
            raise IndexError('Locataion ID not found.')
        else:
            raise TypeError('An integer Station ID must be passed.')

    def __repr__(self):
        return '<Location: %i: %s>' % (self.id, self.name)


class Station():

    url = 'https://acnutrition.amherst.edu/NetNutrition/1/Unit/' + \
    'SelectUnitFromChildUnitsList'
    re_getid = re.compile('[\D]+(?P<id>\d+)[\D]+')

    def __init__(self, sid, name, dontfetch=False):
        '''
        :param bool dontfetch: Instructs the `fetch_menus` method to do
          nothing because the menu information is already populated.
          This is used in the case of default stations.
        '''
        self.id = sid
        self.name = name
        self.dontfetch = dontfetch

        self.menus = []

    def fetch_menus(self):
        if self.dontfetch:
            return

        postdata = urllib.parse.urlencode({'unitOid': self.id}).encode('utf8')
        r = urllib.request.Request(self.url, postdata, {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
        ' ASP.NET_SessionId=' + COOKIE})
        page = json.loads(urllib.request.urlopen(r).read().decode('utf8'))
        for panel in page['panels']:
            if panel['id'] == 'menuPanel':
                page = bs4.BeautifulSoup(panel['html'])
                break

        menus = page.select('.cbo_nn_menuCell > table')
        for menu in menus:
            datetext = menu.select('tr td')[0].get_text()
            for timeofday in menu.select('.cbo_nn_menuLink'):
                mid = int(
                    re.match(self.re_getid, timeofday.get('onclick')
                ).group('id'))
                self.menus.append(Menu(mid, datetext, timeofday.get_text()))
        if len(menus) == 0:
            # it is a station with a permanent menu
            self.menus.append(Menu(self.id, "0", "0"))

    def get_menu(self, menuid):
        if not self.menus:
            raise IndexError('No menus found. Did you fetch them?')
        if isinstance(menuid, int):
            for menu in self.menus:
                if menu.id == menuid:
                    return menu
            return IndexError('Menu ID not found.')
        else:
            raise TypeError('An integer Menu ID must be passed')

    def __repr__(self):
        return '<Location: %i: %s>' % (self.id, self.name)


class Menu():

    url = 'https://acnutrition.amherst.edu/NetNutrition/1/Menu/SelectMenu'
    re_getid = re.compile('[\D]+(?P<id>\d+)[\D]+\d+[\D+]')

    def __init__(self, mid, datetext, timeofday):
        self.id = mid
        self.datetext = datetext
        self.timeofday = timeofday
        self.stuff = []
        self.items = []

    def fetch_menu(self):
        if self.id == 0:
            # station is really a menu...
            postdata = urllib.parse.urlencode({'unitOid': self.id}).encode('utf8')

            return
        postdata = urllib.parse.urlencode({'menuOid': self.id}).encode('utf8')
        r = urllib.request.Request(self.url, postdata, {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
        ' ASP.NET_SessionId=' + COOKIE})
        page = json.loads(urllib.request.urlopen(r).read().decode('utf8'))
        for panel in page['panels']:
            if panel['id'] == 'itemPanel':
                page = bs4.BeautifulSoup(panel['html'])
                break

        items = page.select('.cbo_nn_itemPrimaryRow') + \
            page.select('.cbo_nn_itemAlternateRow')
        for item in items:
            subsel = item.select('.cbo_nn_itemHover')[0]
            name = subsel.get_text()
            iid = int(re.match(self.re_getid, subsel.get('onmouseover')).group('id'))
            serving = item.select('td')[2].get_text()
            stuff = [i.get_text() for i in item.select('td')]
            self.items.append(Item(iid, name, serving, stuff))
            #   , price))

    fetch_items = fetch_menu  # interface consistency
    
    def fetch_test(self):
        postdata = urllib.parse.urlencode({'menuOid': self.id}).encode('utf8')
        r = urllib.request.Request(self.url, postdata, {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
        ' ASP.NET_SessionId=' + COOKIE})
        page = json.loads(urllib.request.urlopen(r).read().decode('utf8'))
        for panel in page['panels']:
            if panel['id'] == 'itemPanel':
                return(bs4.BeautifulSoup(panel['html']))

        
#    def fetch_page(self):
#        postdata = urllib.parse.urlencode({'menuOid': self.id}).encode('utf8')
#        r = urllib.request.Request(self.url, postdata, {
#        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#        'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
#        ' ASP.NET_SessionId=' + COOKIE})
#        return(urllib.request.urlopen(r).read().decode('utf8'))
            
    def __repr__(self):
        return '<Menu: %i: %s: %s>' % (self.id, self.datetext, self.timeofday)


class Item():
    url = 'https://acnutrition.amherst.edu/NetNutrition/1/ShowItemNutritionLabel'
    def __init__(self, iid, name, servingsize, stuff):
        self.id = iid
        self.name = name
        self.servingsize = servingsize
        
    def fetch_nutrition(self):
        r = requests.get('https://acnutrition.amherst.edu/NetNutrition/' + \
                    '1/NutritionDetail/ShowItemNutritionLabel',
            params={'detailOid': self.id},
            headers={'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;'+\
                        ' ASP.NET_SessionId=' + COOKIE}
                        )
        page = bs4.BeautifulSoup(r.text)
        nutrition = []
        for i in page.find_all('table'):
            if '%' not in i.text:
                if ':' in i.text:
                    nutrition.append(i.text.replace(u'\xa0', u' ').strip())
        nutrition = {i.split(':')[0].strip():i.split(':')[1] for i in nutrition}
        self.nutrition = nutrition
        
        
        

    def __repr__(self):
        return '<Item {} {} {}>'.format(self.id, self.name, self.servingsize)