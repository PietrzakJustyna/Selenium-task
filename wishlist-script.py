# We assume that the script user has python 3.7 or higher with Selenium installed and a geckodriver available.

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import urllib.request
import argparse
import os
import json


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def iterate_wishlist(wishlist):
    for product in wishlist:
        title = product.find_element_by_class_name("product-title__text").get_attribute('innerHTML')
        price = product.find_element_by_class_name("_price.product-state__price").get_attribute('innerHTML')
        result[args.username]["wishlist"][title] = price
        if is_float(price):
            global price_sum
            price_sum += float(price)


if __name__ == "__main__":

    if not os.path.exists('avatars'):
        os.makedirs('avatars')

    if not os.path.exists('json_results'):
        os.makedirs('json_results')

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help="Give the username of user that interests you", required=True)
    args = parser.parse_args()

    driver = webdriver.Firefox()
    driver.get(f'https://www.gog.com/u/{args.username}/wishlist')
    time.sleep(5)

    try:
        avatar = driver.find_element_by_class_name("avatar") \
            .get_attribute("srcset") \
            .split(",")[1] \
            .strip() \
            .split(" ")[0]
    except NoSuchElementException:
        print("No data for such username.")
        driver.close()
        exit(0)

    result = {args.username: {}}
    result[args.username]["wishlist"] = {}
    price_sum = 0

    try:
        paginaiton = driver.find_element_by_class_name("list-navigation__pagin")
        total_pages = paginaiton.find_element_by_class_name("pagin__total").get_attribute('innerHTML')
        wishlist = driver.find_elements_by_class_name("product-row-wrapper")
        iterate_wishlist(wishlist)

        for _ in range(int(total_pages)-1):
            next_page = paginaiton.find_element_by_class_name("pagin__next")
            next_page.click()
            time.sleep(5)
            wishlist = driver.find_elements_by_class_name("product-row-wrapper")
            iterate_wishlist(wishlist)

    except NoSuchElementException:
        wishlist = driver.find_elements_by_class_name("product-row-wrapper")
        iterate_wishlist(wishlist)

    result[args.username]["sum"] = round(price_sum, 2)
    time.sleep(5)
    driver.close()

    path = f"./avatars/{args.username}.jpg"
    urllib.request.urlretrieve(avatar, path)
    result[args.username]["avatar_location"] = path

    with open(f'./json_results/{args.username}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
