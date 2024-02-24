import utils.utils
from config.config import API_URL, API_KEY
from telebot.custom_filters import StateFilter
from telebot.types import Message, BotCommand, CallbackQuery
from telebot.apihelper import ApiTelegramException
from loguru import logger
from utils.api import api
from states.states import UserStateInput, UserStateInfo
import requests
from loader import bot
from keyboards.keyboard import show_cities_keyboard, sorting_keyboard
from utils.utils import is_int

city_id = []
quantity = []
messages = []

button = bot.set_my_commands([BotCommand('city_selection', 'Ввести город'),
                              BotCommand('date_change', 'Сменить даты'),
                              BotCommand('sorting', 'Изменить сортировку'),
                              BotCommand('history', 'Последние 5 запросов')])


@bot.message_handler(commands=['history'])
def history_cmd(message: Message) -> None:
    """
    Обработчик команды /history
    Выводит последние 5 запросов пользователя
    :param message:
    :return:
    """
    bot.set_state(message.chat.id, UserStateInfo.history)
    try:
        bot.send_message(message.from_user.id, 'История ваших последних 5 запросов:')
        bot.send_message(message.from_user.id, '\n'.join(messages))
    except ApiTelegramException:
        bot.send_message(message.chat.id, 'Возникла ошибка 😕'
                                          '\nВыберите другую команду')


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """
    Обработчик команды /start
    Приветствует пользователя, запоминает необходимые данные и спрашивает - какой искать город.
    :param message : Message
    :return : None
    """
    bot.send_message(message.chat.id, text=f"✌ Привет, {message.from_user.first_name}")
    bot.set_state(message.chat.id, UserStateInput.command)
    bot.set_state(message.chat.id, UserStateInfo.name)
    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        quantity.clear()
        logger.info('Запоминаем выбранную команду: ' + message.text + f" User_id: {message.chat.id}")
        data['command'] = message.text
        data['sort'] = check_command(message.text)
        data['chat_id'] = message.chat.id
    bot.set_state(message.chat.id, UserStateInput.city_insert)
    bot.send_message(message.from_user.id, "🧳 Введите город, в котором ищем:")


@bot.message_handler(commands=['city_selection'])
def select_city(message: Message) -> None:
    """
    Обработчик команд, срабатывает на команду /city_selection
    и запоминает необходимые данные. Спрашивает пользователя - какой искать город.
    :param message : Message
    :return : None
    """
    bot.set_state(message.chat.id, UserStateInput.command)
    with bot.retrieve_data(message.chat.id) as data:
        data.clear()
        quantity.clear()
        logger.info('Запоминаем выбранную команду: ' + message.text + f" User_id: {message.chat.id}")
        data['command'] = message.text
        data['sort'] = check_command(message.text)
        data['chat_id'] = message.chat.id
    bot.set_state(message.chat.id, UserStateInput.city_insert)
    bot.send_message(message.from_user.id, "🧳 Введите город, в котором ищем:")


@bot.message_handler(state=UserStateInput.city_insert)
def city_insert(message: Message) -> None:
    """
    Записывает введенный пользователем город, запускает функцию get_city
    и предлагает выбрать город на кнопках
    :param message : Message
    :return : None
    """
    with bot.retrieve_data(message.chat.id) as data:
        data['city_insert'] = message.text
        logger.info(f'Введён город {message.text}')
        if len(messages) >= 5:
            messages.pop(0)
            messages.append(message.text)
        else:
            messages.append(message.text)
        cities_url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
        cities_querystring = {"name": message.text, "locale": "ru"}

        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": API_URL
        }
        response_cities = requests.get(cities_url, params=cities_querystring, headers=headers)
        logger.info('Сервер ответил: ' + str(response_cities.status_code) + f' User_id: {message.chat.id}')
        try:
            true_cities = api.get_city(response_cities.text)
        except LookupError:
            bot.send_message(message.from_user.id, 'Ничего не найдено.')
            bot.set_state(message.chat.id, UserStateInput.city_insert)
            bot.send_message(message.from_user.id, "🧳 Введите город, в котором ищем:")
        bot.send_message(message.from_user.id, '🔽 Выберите город 🔽',
                         reply_markup=show_cities_keyboard(message, true_cities))
        if None:
            bot.send_message(message.chat.id, 'Ничего не найдено.'
                                              '\nПопробуйте команду выбора города заново')
        bot.set_state(message.chat.id, UserStateInfo.city)


@bot.callback_query_handler(lambda c: is_int(c.data))
def destination_id_callback(call: CallbackQuery) -> None:
    """
    Реагирует на выбор города пользователем и спрашивает
    количество отелей, которое необходимо вывести

    :param call:
    :return : None
    """
    logger.info('Пользователь выбрал город')
    city_id.clear()
    city_id.append(call.data)
    if call.data:
        bot.set_state(call.message.chat.id, UserStateInput.destination_id)
        with bot.retrieve_data(call.message.chat.id) as data:
            data['destination_id'] = call.data
        bot.set_state(call.message.chat.id, UserStateInput.hotels_amount)
        bot.send_message(call.message.chat.id, 'Сколько отелей предложить? (не более 15)')


@bot.message_handler(state=UserStateInput.hotels_amount)
def input_quantity(message: Message) -> None:
    """
    Ввод количества выдаваемых на странице отелей, а так же проверка, является ли
    введённое числом и входит ли оно в заданный диапазон от 1 до 15
    :param message : Message
    :return : None
    """
    if message.text.isdigit():
        if 0 < int(message.text) <= 15:
            logger.info('Ввод и запись количества отелей: ' + message.text + f' User_id: {message.chat.id}')
            with bot.retrieve_data(message.chat.id) as data:
                data['quantity_hotels'] = message.text
                if len(messages) >= 5:
                    messages.pop(0)
                    messages.append(message.text)
                else:
                    messages.append(message.text)
            bot.set_state(user_id=message.chat.id, state=UserStateInput.date_in)
            bot.send_message(message.from_user.id,
                             '🗓 Введите дату ***заселения*** в отель'
                             '\n(в числовом формате "месяц-день"):', parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, 'Ошибка! Это должно быть число в диапазоне от 1 до 15! Повторите ввод!')
    else:
        bot.send_message(message.chat.id, 'Ошибка! Вы ввели не число! Повторите ввод!')
    quantity.append(message.text)


@bot.message_handler(state=UserStateInput.date_in)
def in_date(message: Message) -> None:
    """
    Запрашивает у пользователя дату выезда из отеля
    :param message : Message
    :return : None
    """
    logger.info('Ввод даты заселения в отель')
    api.inn_date = message.text
    if len(messages) >= 5:
        messages.pop(0)
        messages.append(message.text)
    else:
        messages.append(message.text)
    bot.set_state(user_id=message.chat.id, state=UserStateInput.date_out)
    bot.send_message(message.from_user.id, '🗓 Введите дату ***выезда***'
                                           '\n(в числовом формате "месяц-день"):', parse_mode='Markdown')


@bot.message_handler(state=UserStateInput.date_out)
def out_date(message: Message) -> None:
    """
    Записывает дату выезда из отеля и
    предлагает пользователю три способа сортировки в виде кнопок

    :param message : Message
    :return : None
    """
    logger.info('Ввод даты выезда из отеля')
    api.outt_date = message.text
    if len(messages) >= 5:
        messages.pop(0)
        messages.append(message.text)
    else:
        messages.append(message.text)
    bot.set_state(user_id=message.chat.id, state=UserStateInput.sort)
    bot.send_message(message.from_user.id, '↕ Выберите способ сортировки',
                     reply_markup=sorting_keyboard(message))


@bot.message_handler(commands=['date_change'])
def date_changing(message: Message) -> None:
    """
    Реагирует на команду date_change для изменения даты заселения
    и запрашивает новую дату
    :param message:
    :return:
    """
    logger.info('Ввод новой даты заезда в отель')
    if len(messages) >= 5:
        messages.pop(0)
        messages.append(message.text)
    else:
        messages.append(message.text)
    bot.set_state(user_id=message.chat.id, state=UserStateInput.date_in)
    bot.send_message(message.from_user.id, '🗓 Введите дату ***заселения*** в отель\n(в числовом формате '
                                           '"месяц-день"):', parse_mode='Markdown')


@bot.message_handler(state=UserStateInput.sort)
def sort_choice(message: Message) -> None:
    """
    Предлагает пользователю три способа сортировки в виде кнопок

    :param message : Message
    :return : None
    """
    logger.info('Выбор способа сортировки')
    bot.send_message(message.from_user.id, '↕ Выберите способ сортировки ↕',
                     reply_markup=sorting_keyboard(message))


@bot.callback_query_handler(lambda c: c.data.isalpha())
def sort_callback(call: CallbackQuery) -> None:
    """
    Реагирует на выбор сортировки пользователем и запускает функцию take_hotels
    в случае возникновения ошибки KeyError заново запрашивает дату заселения у пользователя

    :param call:
    :return : None
    """
    api.srt = call.data
    try:
        take_hotels(call.message)
    except KeyError:
        bot.send_message(call.message.chat.id, 'Неверный формат даты.')
        bot.set_state(user_id=call.message.chat.id, state=UserStateInput.date_in)
        bot.send_message(call.message.chat.id, '🗓 Введите дату ***заселения*** в отель\n(в числовом формате '
                                               '"месяц-день"):', parse_mode='Markdown')


@bot.message_handler(state=UserStateInput.hotels)
def take_hotels(message: Message) -> None:
    """
    Выполняет поиск отелей с учетом ранее выбранных действий

    :param message : Message
    :return : None
    """
    logger.info('Поиск отелей по id')
    try:
        hotels_dict = api.get_hotels(city_id[0])
        if hotels_dict:
            bot.send_message(message.chat.id, text='✔ Список отелей под ваши предпочтения:')
            count = 0
            for name, kind in hotels_dict.items():
                bot.send_message(message.chat.id, f'🛎 Отель: {name}\n🛅 Тип: {kind}')
                count += 1
                if count == int(quantity[0]):
                    break
        else:
            bot.send_message(message.chat.id, 'К сожалению, отсутствуют отели по вашим критериям 😕'
                                              '\nПопробуйте ввести другой город')
            select_city(message)
        bot.send_message(message.chat.id, 'Конец результатов поиска.')
        bot.send_message(message.chat.id, text='Переходите по ссылке, бронируйте или\n👇 Выберите команду из меню')
    except IndexError:
        bot.send_message(message.chat.id, 'Возникла ошибка 😕'
                                          '\nПопробуйте команду выбора города заново')


@bot.message_handler(commands=['sorting'])
def sort_command(message: Message) -> None:
    """
    Смена способа сортировки
    :param message : Message
    :return : None
    """
    logger.info('Смена способа сортировки')
    bot.set_state(user_id=message.chat.id, state=UserStateInput.sort)


def check_command(command: str) -> str:
    """
    Проверка команды и назначение параметра сортировки

    :param command : str
    :return : str
    """
    if command == '/sorting':
        return 'PRICE_LOW_TO_HIGH'
    elif command == '/date_change':
        return 'DATE_CHANGED'
    elif command == '/city_selection':
        return 'CITY_SELECTED'
    elif command == '/history':
        return 'HISTORY_RETURNED'


if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    api.set_default_commands(bot)
    bot.infinity_polling()
