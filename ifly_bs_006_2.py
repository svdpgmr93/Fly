from selenium import webdriver
import time
import math
import requests
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
import json

in_origin = 'Odessa'
origin_code = 'ODS'
in_destination = 'Kyiv'
destination_code = 'KBP'
in_first_date = '01.07.2021'
in_second_date = '30.07.2021'


def input_cities_dates(driver, o_city, o_code, d_city, d_code, o_date, d_date):
    # If d_date is None (second date), then script find an press "One Way" button
    if d_date is None:
        driver.find_element_by_class_name('field-part.fly-from').find_element_by_class_name('title').click()
        a = driver.find_element_by_id('id-input-from-0')
        a.send_keys(o_city)
        time.sleep(2)
        try:
            a1 = driver.find_element_by_class_name('ui-autocomplete.ui-menu.ui-widget.ui-widget-content.ui-corner-all.airports-autocomplete').find_elements_by_class_name('code')
            for elem in a1:
                if elem.text == o_code:
                    elem.click()
                    break
                else:
                    pass
        except NoSuchElementException:
            pass
        # a.send_keys(Keys.ENTER)
        driver.find_element_by_class_name('field-part.fly-to').click()
        b = driver.find_element_by_id('id-input-to-0')
        b.send_keys(d_city)
        time.sleep(2)
        try:
            a1 = driver.find_element_by_id('ui-id-6').find_elements_by_class_name('code')
            for elem in a1:
                if elem.text == d_code:
                    elem.click()
                    break
                else:
                    pass
        except NoSuchElementException:
            pass
        # b.send_keys(Keys.ENTER)
        c = driver.find_element_by_id('id-date-0')
        c.send_keys(o_date)
        c.send_keys(Keys.ENTER)
        time.sleep(1)
    else:
        driver.find_element_by_class_name('field-part.fly-from').find_element_by_class_name('title').click()
        a = driver.find_element_by_id('id-input-from-0')
        a.send_keys(o_city)
        a.send_keys(Keys.ENTER)
        time.sleep(3)
        driver.find_element_by_class_name('field-part.fly-to').click()
        b = driver.find_element_by_id('id-input-to-0')
        b.send_keys(d_city)
        time.sleep(3)
        b.send_keys(Keys.ENTER)
        time.sleep(3)
        c = driver.find_element_by_id('id-date-0')
        c.send_keys(o_date)
        c.send_keys(Keys.ENTER)
        time.sleep(1)
        d = driver.find_element_by_id('id-date-1')
        d.send_keys(d_date)
        d.send_keys(Keys.ENTER)
        time.sleep(1)


def main_(o_city, o_code, d_city, d_code, o_date, d_date=None):
    start_time = time.time()
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    web_dr = webdriver.Chrome()
    web_dr.maximize_window()
    web_dr.get('https://ifly.ua/en/')
    if d_date is None:
        web_dr.find_element_by_class_name('one-way').click()
        time.sleep(1)
    input_cities_dates(driver=web_dr, o_city=o_city, o_code=o_code, d_city=d_city, d_code=d_code, o_date=o_date, d_date=d_date)
    web_dr.find_element_by_class_name('submit-button').click()
    check = double_waits(driver=web_dr, time_to_error=40)
    if check == 0:
        return 'Error'
    elif check == 2:
        return []
    else:
        paginator(driver=web_dr)
        page = web_dr.page_source
        output_data = parse_4(page=page, currency=get_currency())
        finish_time = time.time()
        print(finish_time - start_time)
        with open('data.json', 'w', encoding='UTF-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
        # web_dr.close()
        print('good')
        return json.dumps(output_data, ensure_ascii=False)


def paginator(driver):
    try:
        while driver.find_element_by_class_name('paging-more-btn.button-blue'):
            a = driver.find_element_by_class_name('paging-more-btn.button-blue')
            a.click()
            time.sleep(2)
            a.send_keys(Keys.PAGE_UP)
    except ElementNotInteractableException:
        pass


def parse_4(page, currency):
    soup = BeautifulSoup(page, 'html.parser')
    serch_result = soup.find('div', {'class': 'offers-list active'})
    offers = serch_result.find_all("div", {'class': 'offer'})
    tickets = []
    for offer in offers:
        price = offer.find('strong', {'class': 'value'}).find('span', {'class': 'price-value'})
        price = str(price.string)
        price = int(''.join(price.split(' '))) / currency
        sectors = offer.find_all('li', {'class': 'sector'})
        out_sectors = get_sectors(sectors)
        ticket = {'price': (str(math.ceil(price)) + ' USD'), 'sectors': out_sectors}
        tickets.append(ticket)
    return tickets


def get_sectors(sectors):
    out_sectors = {}
    if len(sectors) == 1:
        full_views = sectors[0].find_all('div', {'class': 'full-view'})
        out_sectors['fly_to'] = get_variants(full_views=full_views)
    else:
        full_views = sectors[0].find_all('div', {'class': 'full-view'})
        out_sectors['fly_to'] = get_variants(full_views=full_views)
        full_views = sectors[1].find_all('div', {'class': 'full-view'})
        out_sectors['fly_return'] = get_variants(full_views=full_views)
    return out_sectors


def get_variants(full_views):
    variants = []
    for full_view in full_views:
        out_full_view = {}
        way_points = full_view.find_all('div', {'class': 'way-point'})
        out_way_points = get_data_from_way_points(way_points)
        out_full_view['first_wp'] = out_way_points[0]
        out_full_view['waypoints'] = out_way_points[1]
        out_full_view['last_wp'] = out_way_points[2]
        variants.append(out_full_view)
    return variants


def get_data_from_way_points(wps):
    waypoint_first = {}
    waypoint_last = {}
    waypoints = []
    for i in range(len(wps)):
        if i == 0:
            waypoint_first['origin_time'] = wps[i].find('div', {'class': 'datetime'}).get('title')
            city = wps[i].find('div', {'class': 'departure destination'}).find('strong', {'class': 'title'})
            waypoint_first['origin_city'] = city.text.strip()
            origin_airport = wps[i].find('div', {'class': 'departure destination'}).find('em', {'class': 'sub-title'})
            waypoint_first['origin_airport'] = origin_airport.text.strip()
            plane = wps[i].find('div', {'class': 'flight-info'}).find('span', {'class': 'euqipment'})
            waypoint_first['plane'] = plane.text.strip()
            waypoint_first['flight_number'] = wps[i].find('span', {'class': 'flt_nbr'}).text.strip()
        elif i == (len(wps) - 1):
            waypoint_last['departure_time'] = wps[i].find('div', {'class': 'datetime'}).get('title')
            waypoint_last['departure_city'] = wps[i].find('div', {'class': 'arrival destination'}).find('strong', {'class': 'title'}).text.strip()
            waypoint_last['departure_airport'] = wps[i].find('div', {'class': 'arrival destination'}).find('em', {'class': 'sub-title'}).text.strip()
        else:
            wp = {}
            wp['arrival_time'] = wps[i].find('div', {'class': 'datetime transfer-datetime'}).find('div', {'class': 'short-time arrival-time'}).get('data-tooltip')
            wp['departure_time'] = wps[i].find('div', {'class': 'datetime transfer-datetime'}).find('div', {'class': 'short-time departure-time'}).get('data-tooltip')
            wp['wait_time'] = wps[i].find('em', {'class': 'stop-duration'}).text.split()
            a = ''
            for elem in wp['wait_time']:
                a += elem.strip()
            wp['wait_time'] = a
            wp['transfer_airport'] = wps[i].find('strong', {'class': 'title'}).text.strip() + ' ' + wps[i].find('em', {'class': 'sub-title'}).text.strip()
            wp['flight_number'] = wps[i].find('span', {'class': 'flt_nbr'}).text.strip()
            plane = wps[i].find('div', {'class': 'flight-info'}).find('span', {'class': 'euqipment'})
            wp['plane'] = plane.text.strip()
            waypoints.append(wp)
    a = (waypoint_first, waypoints, waypoint_last)
    return a


def double_waits(driver, time_to_error):
    waits_time = 0
    while True:
        try:
            driver.find_element_by_id('all-flights').find_element_by_class_name('offer')
            return 1
        except NoSuchElementException:
            pass
        try:
            driver.find_element_by_id('all-flights').find_element_by_class_name('empty-message.active')
            return 2
        except NoSuchElementException:
            pass
        time.sleep(0.5)
        waits_time += 0.5
        if waits_time >= time_to_error:
            return 0


def get_currency():
    url = 'https://finance.i.ua/'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    currency_usd_list = soup.find('tbody').find('tr').find_all('span', {'class': 'value'})
    currency_usd_list_2 = []
    for i in currency_usd_list:
        value = i.text
        currency_usd_list_2.append(value)
    nbu_usd = float(currency_usd_list_2[2][0:5])
    return nbu_usd


print(main_(o_city=in_origin, o_code=origin_code, d_city=in_destination, d_code=destination_code, o_date=in_first_date))
