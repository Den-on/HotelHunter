import json
from typing import Dict
import requests
from telebot.types import BotCommand
from config import DEFAULT_COMMANDS

inn_date = ''
outt_date = ''
srt = ''


def set_default_commands(bot):
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )


def get_city(response_text: str) -> Dict:
    true_cities = {}
    data = json.loads(response_text)
    if not data:
        raise LookupError('Пустой запрос.')
    for i in range(len(data)):
        if data[i]['type'] == 'ci':
            true_cities[data[i]['dest_id']] = data[i]['label']
    return true_cities


def get_hotels(city_id: str) -> Dict:
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    querystring = {"units": "metric", "dest_id": city_id, "dest_type": "city", "room_number": "1",
                   "checkin_date": '2024-' + inn_date, "order_by": srt, "locale": "ru", "adults_number": "2",
                   "checkout_date": '2024-' + outt_date, "filter_by_currency": "RUB"}
    headers = {
        "X-RapidAPI-Key": "4b9fd7a28bmsh7f334e0c422fd45p1a1f13jsn6ad014626ee6",
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring).json()
    out = response['result']
    types = ['Отель', 'Гостевой дом', 'Хостел', 'Апартаменты/квартира', 'Капсульный отель']
    hotels_data = {}
    for i in range(len(out)):
        if out[i]['accommodation_type_name'] in types:
            hotels_data[out[i]['hotel_name']] = out[i]['accommodation_type_name'] + \
                                                '\n💲 Стоимость: ' + str(out[i]['min_total_price']) + ' ' \
                                                + str(out[i]['currency_code']) + '\n' + out[i]['url']
            print(out)
    return hotels_data
