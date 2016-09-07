
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 16:21:17 2016
The Wok2 library is used to navigate and download menus from
Amherst College's NetNutrition dining menu pages.
@author: steven
"""
import json
import urllib.request
import urllib.parse
import re
import bs4
import requests
#%%
def get_cookie():
    """Returns a cookie for a sesssion in NetNutrition"""
    url = 'https://acnutrition.amherst.edu/NetNutrition/1'
    session = requests.Session()
    session.get(url)
    return session.cookies.get_dict()['ASP.NET_SessionId']

URL = 'https://acnutrition.amherst.edu/NetNutrition/1'

class MainPage(object):
    """
    An object representing the splash page of the NetNutrition web portal.

    Attributes:
        url: the url of the NetNutrition splash page
        sidebar: Location and Menu objects representing the dining locations
        and station menus in the sidebar buttons on the NetNutrition splash
        page
    """
    re_getid = re.compile(r'[\D]+(?P<id>\d+)[\D]+')

    def __init__(self):
        self.sidebar = []

    def fetch_sidebar(self):
        """
        Selects all units in the sidebar
        """
        req = urllib.request.Request(URL, None, DATA)
        page = bs4.BeautifulSoup(urllib.request.urlopen(req))
        locations = page.select('.cbo_nn_sideUnitCell a')

        self.sidebar = []  # Clear out and repopulate the list
        for loc in locations:
            name = loc.get_text()
            lid = int(re.match(self.re_getid, loc.get('onclick')).group('id'))
            self.sidebar.append(MenuSchedule(lid, name))

    def fetch_recursively(self):
        """fetches all menu schedules, menus, and items"""
        self.fetch_sidebar()
        for menu_schedule in self.sidebar:
            menu_schedule.fetch_menus()
            for menu in menu_schedule.menus:
                menu.fetch_items()
                for item in menu.items:
                    item.fetch_nutrition()


    def get_location(self, loc):
        """Requests, returns a location in the sidebar by id"""
        if not self.sidebar:
            raise IndexError('You have not fetched any sidebar units')
        if isinstance(loc, int):
            for location in self.sidebar:
                if location.id == loc:
                    return location
            raise IndexError('Location ID not found.')
        else:
            raise TypeError('An integer Location ID must be passed.')

#class unit(Wok):
#    def __init__(self, unit_id, name):
#        self.id = unit_id
#        self.name = name

class MenuSchedule(object):
    """
    An object representing a unit in the main sidebar.  Can be Default:0,
    indicating the unit is a default station.

    Attributes:
        url: the NetNutrition url from which sidebar units may be selected
        id: the location id (position on the sidebar, starting at 1)
        name: the string location name
        menus: Menu objects.
    """
    url = URL + '/Unit/SelectUnitFromSideBar'
    re_getid = re.compile(r'[\D]+(?P<id>\d+)[\D]+')

    def __init__(self, lid, name):
        self.lid = lid
        self.name = name
        self.menus = []

    def get_unit(self, unit_id):
        """
        Fetches an id'd unit from the page
        Args:
            unit_id: the unit id of the unit to be fetched
        Returns:
            a json-formatted dict of the page fetched
        """
        postdata = urllib.parse.urlencode({'unitOid': unit_id}).encode('utf8')
        req = urllib.request.Request(self.url, postdata, DATA)
        return json.loads(urllib.request.urlopen(req).read().decode('utf8'))

    def fetch_menus(self):
        """
        Fetches all menus presnt in the menu schedule page. If the page
        represents a default station, this method returns a default Menu object
        populated with items
        """
        dlpage = self.get_unit(self.lid)
        for panel in dlpage['panels']:
            if panel['id'] == 'menuPanel':
                if panel['html']:
                    # This is a menu schedule
                    page = bs4.BeautifulSoup(panel['html'])
                    self.menus = []  # Clear out and repopulate the list
                    for menu in page.select('.cbo_nn_menuCell > table'):
                        datetext = menu.select('tr td')[0].get_text()
                        for timeofday in menu.select('.cbo_nn_menuLink'):
                            mid = int(
                                re.match(
                                    self.re_getid,
                                    timeofday.get('onclick')).group('id')
                            )
                            self.menus.append(Menu(mid,
                                                   datetext,
                                                   timeofday.get_text()))
                else:
                    #This is a default station
                    for panel in dlpage['panels']:
                        if panel['id'] == 'itemPanel' and panel['html']:
                            page = bs4.BeautifulSoup(panel['html'])
                    default_menu = Menu(0, "Default", "Default", dontfetch=True)
                    items = page.select('.cbo_nn_itemPrimaryRow') + \
                    page.select('.cbo_nn_itemAlternateRow')
                    for item in items:
                        subsel = item.select('.cbo_nn_itemHover')[0]
                        name = subsel.get_text()
                        iid = int(
                            re.match(
                                self.re_getid,
                                subsel.get('onmouseover')
                                ).group('id')
                        )
                        serving_size = item.select('td')[2].get_text()
                        default_menu.items.append(Item(iid, name, serving_size))
                    self.menus.append(default_menu)

    def get_menu_schedule(self, mid):
        "Fetches all menu schedules in the main page sidebar"
        if not self.menus:
            raise IndexError('You have not fetched any menus')
        if isinstance(mid, int):
            for menu in self.menus:
                if menu.id == mid:
                    return menu
            raise IndexError('Locataion ID not found.')
        else:
            raise TypeError('An integer Station ID must be passed.')

    def __repr__(self):
        return '<Menu Schedule: %i: %s>' % (self.lid, self.name)


class Menu(object):
    """

    Attributes:
        mid: id of the menu
        name: name of the menu
        datetext: the date in the format 'Weekday, Month DD, YYYY'
        timeofday: 'Breakfast', 'Lunch', 'Dinner', or for default stations,
        'Always'.
        dontfetch: Instructs the `fetch_menus` method to do nothing because
        the menu information is already populated. This is used in the case
        of default stations.
    """
    url = URL + '/Menu/SelectMenu'
    re_getid = re.compile(r'[\D]+(?P<id>\d+)[\D]+')
    def __init__(self, mid, datetext, timeofday, dontfetch=False):
        '''
        Args:
            mid: id of the menu
            name: name of the menu
            datetext: the date in the format 'Weekday, Month DD, YYYY'
            timeofday: 'Breakfast', 'Lunch', 'Dinner', or for default stations,
            'Always'.
            dontfetch: Instructs the `fetch_menus` method to do nothing because
            the menu information is already populated. This is used in the case
            of default stations.
        '''
        self.mid = mid
        self.datetext = datetext
        self.timeofday = timeofday
        self.items = []
        self.dontfetch = dontfetch

    def fetch_items(self):
        "Fetches all items in the menu"
        if self.dontfetch:
            return
        postdata = urllib.parse.urlencode({'menuOid': self.mid}).encode('utf8')
        req = urllib.request.Request(self.url, postdata, DATA)
        dlpage = json.loads(urllib.request.urlopen(req).read().decode('utf8'))
        for panel in dlpage['panels']:
            if panel['id'] == 'itemPanel' and panel['html']:
                page = bs4.BeautifulSoup(panel['html'])
        items = page.select('.cbo_nn_itemPrimaryRow') + \
        page.select('.cbo_nn_itemAlternateRow')
        for item in items:
            subsel = item.select('.cbo_nn_itemHover')[0]
            name = subsel.get_text()
            iid = int(re.match(self.re_getid,
                               subsel.get('onmouseover')).group('id'))
            serving_size = item.select('td')[2].get_text()
            self.items.append(Item(iid, name, serving_size))

    def get_item(self, iid):
        """Gets an item in menu.items by id"""
        if not self.items:
            raise IndexError('No menus found. Did you fetch them?')
        if isinstance(iid, int):
            for menu in self.items:
                if menu.id == iid:
                    return menu
            return IndexError('Menu ID not found.')
        else:
            raise TypeError('An integer Menu ID must be passed')

    def __repr__(self):
        return '<Menu: %i: %s: %s>' % (self.mid, self.datetext, self.timeofday)

class Item(object):
    """
    A food item
    Attributes:
        iid: the item id with which to fetch item nutrition
        name: the string name of the food item
        servingsize: the string serving size quantity
        nutrition: a dict mapping each nutrient to its value (e.g. grams)
    """
    url = URL + '/NutritionDetail/ShowItemNutritionLabel'

    def __init__(self, iid, name, servingsize):
        self.iid = iid
        self.name = name
        self.servingsize = servingsize
        self.nutrition = {}

    def __repr__(self):
        return '<Item %i: %s: %s>' % (self.iid, self.name, self.servingsize)

    def fetch_nutrition(self):
        """
        Fetches this item's nutrition information to populate self.nutrition
        """
        try:
            postdata = urllib.parse.urlencode(
                {'detailOid': self.iid}
            ).encode('utf8')
            req = urllib.request.Request(self.url, postdata, DATA)
            dlpage = urllib.request.urlopen(req).read().decode('utf8')
            if not dlpage:
                print('1')
            page = bs4.BeautifulSoup(dlpage)
            raw_nutrition = []
            for i in page.select('td .cbo_nn_LabelBorderedSubHeader'):
                nutrient_holder = []
                for j in i.select('td'):
                    nutrient_holder.append(j.text.replace(u'\xa0', u' '))
                raw_nutrition.append(nutrient_holder)
            nutrition = {i[0]:i[1] for i in raw_nutrition[0:1]}
            for i in raw_nutrition[1:]:
                try:
                    nutrition[i[1].replace(':', '').strip()] = i[2].strip()
                except IndexError:
                    print('IndexError')
                    print(i)
            self.nutrition = nutrition
        except:
            raise ValueError('Id must be funky')


#%%
if __name__ == '__main__':
    COOKIE = get_cookie()
    DATA = {}
    DATA['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    DATA['Cookie'] = 'CBORD.netnutrition2=NNexternalID=1&Layout=; '
    DATA['Cookie'] += 'ASP.NET_SessionId=' + COOKIE
    MAIN = MainPage()
    MAIN.fetch_sidebar()
    MAIN.sidebar[0].fetch_menus()
    MAIN.sidebar[0].menus[0].fetch_items()
    MAIN.sidebar[0].menus[0].items[0].fetch_nutrition()

