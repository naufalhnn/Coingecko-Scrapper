from httpx import Client
from bs4 import BeautifulSoup
from typing import Any
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time
import os
import pandas as pd


class CoinGeckoSpider(object):
    def __init__(self) -> None:
        self.client = Client()
        self.base_url = 'https://www.coingecko.com/id/all-cryptocurrencies'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        self.headers: dict[str, Any] = {
            'User-Agent': self.user_agent
        }

    def get_pages(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        self.driver.get(self.base_url)

        previous_height = self.driver.execute_script(
            'return document.body.scrollHeight')

        while True:
            time.sleep(10)
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(10)

            try:
                load_more = self.driver.find_element(
                    By.LINK_TEXT, 'Tampilkan Lainnya')
                load_more.click()
                time.sleep(10)
            except NoSuchElementException:
                break

            new_height = self.driver.execute_script(
                'return document.body.scrollHeight')

            if new_height == previous_height:
                break

            previous_height = new_height

        content = self.driver.page_source

        try:
            os.mkdir('temp')
        except FileExistsError:
            pass

        with open('temp/response.html', 'wb' if isinstance(content, bytes) else 'w', encoding='UTF-8') as f:
            f.write(content)

    def get_coins(self):
        with open('temp/response.html', 'r', encoding='UTF-8') as f:
            response = f.read()

        soup = BeautifulSoup(response, 'html.parser')

        table = soup.find(
            'tbody', attrs={'data-target': 'all-coins.tablebody'})

        coins = []

        if table:
            row = table.find_all('tr')
            for item in row:
                try:
                    name = item.find(
                        'span', attrs={'class': 'tw-text-blue-500 tw-font-bold lg:tw-block tw-hidden'}).text
                except:
                    name = '-'

                try:
                    symbol = item.find(
                        'span', attrs={'class': 'tw-hidden d-lg-inline font-normal text-3xs mt-1'}).text
                except:
                    symbol = '-'

                try:
                    price = item.find(
                        'span', attrs={'data-target': 'price.price'}).text
                except:
                    price = '-'

                try:
                    price_1h = item.find(
                        'td', attrs={'class': 'td-change1h'}).span.text
                except:
                    price_1h = '-'

                try:
                    price_24h = item.find(
                        'td', attrs={'class': 'td-change24h'}).span.text
                except:
                    price_24h = '-'

                try:
                    price_7d = item.find(
                        'td', attrs={'class': 'td-change7d'}).span.text
                except:
                    price_7d = '-'

                try:
                    price_30d = item.find(
                        'td', attrs={'class': 'td-change30d'}).span.text
                except:
                    price_30d = '-'

                try:
                    total_volume_24h = item.find(
                        'td', attrs={'class': 'td-total_volume'}).span.text
                except:
                    total_volume_24h = '-'

                try:
                    circulating_supply = item.find(
                        'td', attrs={'class': 'td-circulating_supply'}).div.text
                except:
                    circulating_supply = '-'

                try:
                    total_supply = item.find(
                        'td', attrs={'class': 'td-total_supply'}).div.text
                except:
                    total_supply = '-'

                try:
                    market_cap = item.find(
                        'td', attrs={'class': 'td-market_cap'}).span.text
                except:
                    market_cap = '-'

                data: dict[str, Any] = {
                    'Name': name,
                    'Symbol': symbol,
                    'Price': price,
                    '1h price': price_1h,
                    '24h price': price_24h,
                    '7d price': price_7d,
                    '30d price': price_30d,
                    'Total volume 24h': total_volume_24h,
                    'Circulating supply': circulating_supply,
                    'Total supply': total_supply,
                    'Market cap': market_cap
                }

                coins.append(data)

        # create CSV file
        df = pd.DataFrame(coins)
        df.to_csv('coins.csv', index=False)
        df.to_excel('coins.xlsx', index=False)


if __name__ == '__main__':
    spider = CoinGeckoSpider()
    spider.get_pages()
    spider.get_coins()
