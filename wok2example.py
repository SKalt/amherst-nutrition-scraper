# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 16:40:43 2016

@author: steven
"""
import os
#os.chdir('./amherst-nutrition-scraper')
import wok2
w = wok2.Wok()
#%%
w.fetch_sidebar()
#%%
w.sidebar[0].fetch_stations()
#%%
w.sidebar[0].stations[0].fetch_menus()
#%%
w.fetch_recursively()
#w.locations[0].stations[0].menus[0].fetch_test()
#%%
x=w.locations[0].stations[0].menus[0].fetch_test()
#%%
w.locations[0].stations[0].menus[0].items
#%%
y=w.locations[0].stations[0].menus[0].fetch_page()
#%%
import requests
session = requests.Session()
session.head('https://acnutrition.amherst.edu/NetNutrition/1#')
#%%
response = session.post(
    url='https://acnutrition.amherst.edu/NetNutrition/1/NutritionDetail/ShowItemNutritionLabel',
    data=urllib.parse.urlencode({'detailOid': 351529}).encode('utf8'),
    headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
                ' ASP.NET_SessionId=' + 'gt5c1hn12t2kequxfv2i0qtm'}
)

response.text
#%%
tmp = {
"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
"Cookie":"ASP.NET_SessionId=nws43xshrrw2jz2rhr2vyjmf; CBORD.netnutrition2=NNexternalID=1",
"X-Requested-With":"XMLHttpRequest"}

r=session.post(url='https://acnutrition.amherst.edu/NetNutrition/1/NutritionDetail/ShowItemNutritionLabel',
             data = json.dumps({'detailOid': 351537}),
            headers=tmp)
r.text
#%%
r = requests.get('https://acnutrition.amherst.edu/NetNutrition/1/NutritionDetail/ShowItemNutritionLabel',
             params={'detailOid': 351537},
            headers=tmp)
x = bs4.BeautifulSoup(r.text)
x.text
#%%
headers={
#"Accept":"*/*",
#"Accept-Encoding":"gzip, deflate, br",
#"Accept-Language":"en-US,en;q=0.5",
#"Content-Length":"16",
#"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
"Cookie":"ASP.NET_SessionId=nws43xshrrw2jz2rhr2vyjmf; CBORD.netnutrition2=NNexternalID=1"
#"Host":"acnutrition.amherst.edu",
#"Referer":"https://acnutrition.amherst.edu/NetNutrition/1",
#"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0",
#"X-Requested-With":"XMLHttpRequest"
}
#%%
postdata = urllib.parse.urlencode({'detailOid': 351529}).encode('utf8')
r = urllib.request.Request('https://acnutrition.amherst.edu/NetNutrition/1/ShowItemNutritionLabel',
                           postdata, {
'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=;' + \
' ASP.NET_SessionId=' + 'gt5c1hn12t2kequxfv2i0qtm'})
page = urllib.request.urlopen(r).read().decode('utf8')
#%%
# Fetch the stations at this location
loc = w.get_location(LOCATION_ID)
#%%
loc.fetch_stations()
#%%
station = loc.get_station(STATION_ID)
#%%
# Fetch the available menus at the station (which can vary by meal)
station.fetch_menus()

# Fetch all menus:
for menu in station.menus:
    menu.fetch_items()

for menu in station.menus:
    print('Menu: %s: %s' % (menu.datetext, menu.timeofday))
    for item in menu.items:
        print('  {0:50}{1:20}{2:7}'.format(item.name, item.servingsize, item.price))
#%%
DATA = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
 'Cookie': 'CBORD.netnutrition2=NNexternalID=1&Layout=; ASP.NET_SessionId=2o2ewwqjcdp2l5gfczf5exrx'}
postdata = urllib.parse.urlencode({'unitOid': 19463}).encode('utf8')
r = urllib.request.Request('https://acnutrition.amherst.edu/NetNutrition/1/menu',
                           postdata, DATA)
page = json.loads(urllib.request.urlopen(r).read().decode('utf8'))
#%%