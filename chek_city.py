from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import json
from cities_from_pasha import cities

options = webdriver.ChromeOptions()
options.add_argument('headless')
web_dr = webdriver.Chrome()
web_dr.maximize_window()
web_dr.get('https://ifly.ua/en/')
out_list = []
file = open('bad_cities.json', 'a')

web_dr.find_element_by_class_name('field-part.fly-from').find_element_by_class_name('title').click()
a = web_dr.find_element_by_id('id-input-from-0')
i = 0
for city in cities:
    print(i)
    i += 1
    a.send_keys(city['label'][:-4:])
    time.sleep(1)
    try:
        time.sleep(0.5)
        a2 = web_dr.find_element_by_class_name('field-part.fly-from.filled').find_element_by_class_name('airport-code').text
        if a2 == city['IATA Code']:
            a.clear()
            continue
        else:
            print('Error first', city)
            out_list.append(city)
            a.clear()
            continue
    except NoSuchElementException:
        pass
    try:
        a1 = web_dr.find_element_by_class_name(
            'ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all.airports-autocomplete').find_elements_by_class_name(
            'code')
        a1_text = []
        for elem in a1:
            a1_text.append(elem.text)
        if city['IATA Code'] not in a1_text:
            print('Error second', city)
            out_list.append(city)
        else:
            a.clear()
            continue
    except NoSuchElementException:
        pass
    a.clear()
print(len(out_list))
json.dump(out_list, file)
file.close()
