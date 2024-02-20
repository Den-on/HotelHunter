from telebot import types
from telebot.types import Message, Dict, CallbackQuery, ReplyKeyboardMarkup
from loguru import logger


def show_cities_keyboard(message: Message, true_cities: Dict) -> types.InlineKeyboardMarkup:
    logger.info(f'Вывод кнопок с вариантами городов пользователю. User_id: {message.chat.id}')
    kb_cities = types.InlineKeyboardMarkup()
    for key, value in true_cities.items():
        kb_cities.add(types.InlineKeyboardButton(text=value, callback_data=key))
    return kb_cities


def sorting_keyboard(message: Message) -> types.InlineKeyboardMarkup:
    logger.info(f'Вывод кнопок с вариантами сортировки пользователю. User_id: {message.chat.id}')
    kb_sorting = types.InlineKeyboardMarkup()
    kb_sorting.add(types.InlineKeyboardButton(text='По возрастанию цены', callback_data='price'))
    kb_sorting.add(types.InlineKeyboardButton(text='По отдаленности от центра', callback_data='distance'))
    kb_sorting.add(types.InlineKeyboardButton(text='По популярности', callback_data='popularity'))
    return kb_sorting
