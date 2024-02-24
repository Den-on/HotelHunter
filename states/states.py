from telebot.handler_backends import State, StatesGroup


class UserStateInfo(StatesGroup):
    name = State()
    city = State()
    history = State()


class UserStateInput(StatesGroup):
    command = State()
    city_insert = State()
    destination_id = State()
    hotels_amount = State()
    date_in = State()
    date_out = State()
    sort = State()
    hotels = State()
