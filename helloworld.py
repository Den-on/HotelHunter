from telebot import TeleBot, types
from config import BOT_TOKEN

bot = TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message)
    """
    Функция для создания кнопок
    :param message: 
    :return: 
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/hello-world")
    btn2 = types.KeyboardButton("Привет")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text=f"✌Привет, {message.from_user.first_name}", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_welcome(message):
    """
    Функция для ответа на команду '\hello-world'
    и текст 'Привет'
    :param message:
    :return:
    """
    if message.text == 'Привет':
        bot.send_message(message.chat.id, "Hello world!")
    elif message.text == '/hello-world':
        bot.send_message(message.chat.id, "Hello world!")


if __name__ == '__main__':
    bot.infinity_polling()
