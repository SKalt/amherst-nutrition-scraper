# acnutrition Readme

amherst-nutrition-scraper is a Python module that can be used to download menu data from Amherst College's NetNutrition website. It has the ability to download most of the information, including the list of dining locations, the different stations at each location, the different schedules at those stations (breakfast/lunch/dinner/late night offerings), and finally the actual menu items.

## Usage Example

```python
#! /usr/bin/env python3

import amherst-nutrition-scraper

# get a valid cookie
COOKIE = get_cookie()
print(COOKIE)

# create a data header for future requests
DATA = {}
DATA['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
DATA['Cookie'] = 'CBORD.netnutrition2=NNexternalID=1&Layout=; '
DATA['Cookie'] += 'ASP.NET_SessionId=' + COOKIE

# create an object representing the main page of the NetNutrition site
MAIN = MainPage()
# get MenuSchedule objects representing each schedule of menus in the sidebar. In the
# case of default stations such as 'Beverages', these menu schedules contain default Menu
# objects
MAIN.fetch_sidebar()

# Fetch Val
MAIN.sidebar[0].fetch_menus()

#Fetch breakfast
MAIN.sidebar[0].menus[0].fetch_items()

# Fetch the first item on the menu
MAIN.sidebar[0].menus[0].items[0].fetch_nutrition()

for location in MAIN.sidebar:
  print(location)
for menu in MAIN.sidebar[0]:
  print(menu)
for item in MAIN.sidebar[0].menus[0].items:
  print(item)
print(MAIN.sidebar[0].menus[0].items[0].nutrition)
```