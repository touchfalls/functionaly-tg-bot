import telebot
import random
import string
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from PIL import Image
from config import BOT_TOKEN


bot = telebot.TeleBot(token=BOT_TOKEN)

DEFAULT_PASSWORD_LENGTH = 12
DEFAULT_RANDOM_MIN = 1
DEFAULT_RANDOM_MAX = 100
INTMAX_NUM = 2147483647
SAVE_PUNCTUATION = "!-_$*?"


def flip_coin() -> str:
    return random.choice(["Орёл!", "Решка!"])

def roll_dice() -> str:
    number = random.randint(1, 6)
    dice_emoji = {1: "1️⃣",
                2: "2️⃣",
                3: "3️⃣",
                4: "4️⃣",
                5: "5️⃣",
                6: "6️⃣"}
    return f"Выпало число: {dice_emoji[number]}"

def generate_password(length: int = DEFAULT_PASSWORD_LENGTH) -> str:
    characters = string.ascii_letters + string.digits + SAVE_PUNCTUATION

    password = "".join(random.choices(characters, k=length))

    return (
        f"Ваш пароль ({length} символов): \n\n"
        f"`{password}`\n\n"
        f"👆 Нажмите на пароль, чтобы скопировать"
    )
    
def generate_random(
        min_num: int = DEFAULT_RANDOM_MIN,
        max_num: int = DEFAULT_RANDOM_MAX
        ) -> str:

    number = random.randint(min_num, max_num)

    return f"Случайное число от {min_num} до {max_num}:\n{number}"

@bot.message_handler(commands=['start'])
def cmd_start(message: Message) -> None:

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🪙Монетка", callback_data="action_coin"),
        InlineKeyboardButton("🎲Кубик", callback_data="action_dice"),
        InlineKeyboardButton("🔐Пароль (12)", callback_data="action_password_12"),
        InlineKeyboardButton("🔐Пароль (20)", callback_data="action_password_20"),
        InlineKeyboardButton("🎰Число 1-100", callback_data="action_random"),
        InlineKeyboardButton("🗺️Карта CS2", callback_data="action_maps")
    )

    user_name = message.from_user.username
    first_name = message.from_user.first_name
    
    text = (
        f"Привет, {user_name or first_name}! 👋\n\n"
        f"Я - бот-помощник для быстрых решений \n\n"
        f"🪙/coin - подбросить монетку\n"
        f"🎲/dice - кинуть кубик\n"
        f"🔐/password - сгенерировать пароль\n"
        f"🎰/random - случайное число в диапозоне\n"
        f"🗺️/maps - случайная карта из CS2 для рандомного поиска."
        f"\n"
        f"Попробуй прямо сейчас!"
    )

    bot.reply_to(message=message, text=text, reply_markup=keyboard)

def is_menu_button(call: CallbackQuery):
    return call.data.startswith("action_")

@bot.callback_query_handler(func=is_menu_button)
def handler_callback(call: CallbackQuery):

    chat_id = call.message.chat.id

    if call.data == "action_coin":
        bot.send_message(chat_id=chat_id, text=flip_coin())
    elif call.data == "action_dice":
        bot.send_message(chat_id=chat_id, text=roll_dice())
    elif call.data == "action_password_12":
        bot.send_message(chat_id=chat_id, text=generate_password())
    elif call.data == "action_password_20":
        bot.send_message(chat_id=chat_id, text=generate_password(length=20))
    elif call.data == "action_random":
        bot.send_message(chat_id=chat_id, text=generate_random())
    elif call.data == "action_maps":
        maps = [
            "🐸Ancient",
            "🏝️Anubis",
            "🌴Dust II",
            "🌋Inferno",
            "🏜️Mirage",
            "💣Nuke",
            "🌉Overpass"
        ]

        random_map = random.choice(maps)
        bot.send_message(chat_id=chat_id, text=f"Случайная карта из CS2 для рандомного поиска:\n{random_map}")

    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=['photo'])
def make_black_white(message):
    # Фото принимаем (загружаем себе)
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('before.jpg', 'wb') as file:
        file.write(downloaded_file)

    # Меняем фото (изменение + сохранение изменённого)
    image = Image.open('before.jpg')
    bw_image = image.convert('L')
    bw_image.save('final.jpg')
   
   # Отправка обработанной чб фотки боту
    with open('final.jpg', 'rb') as file:
        bot.send_photo(message.chat.id, file)


@bot.message_handler(commands=['coin'])
def cmd_coin(message: Message) -> None:
    bot.reply_to(message=message, text=flip_coin())

@bot.message_handler(commands=['dice'])
def cmd_dice(message: Message) -> None:
    bot.reply_to(message=message, text=roll_dice())

@bot.message_handler(commands=['password'])
def cmd_password(message: Message) -> None:
    # /password 10 -> password(10)
    # /password 25 -> password(25)
    # /password asd -> Wrong! EXCEPT
    length = DEFAULT_PASSWORD_LENGTH
    parts = message.text.split(" ") # ["/password", "10"]

    if len(parts) == 2:
        length = parts[1]
    try:
        length = int(length)
        if length <= 0:
            raise ValueError
        elif length > INTMAX_NUM:
            length = 100
    except ValueError:
        text = "Формат: /password, /password 50"
    else:
        text = generate_password(length=length)

    bot.reply_to(message=message, text=text, parse_mode="Markdown")

@bot.message_handler(commands=['random'])
def cmd_random(message: Message) -> None:
    parts = message.text.split(" ")

    min_num = DEFAULT_RANDOM_MIN
    max_num = DEFAULT_RANDOM_MAX
    
    try:
        if len(parts) == 3:
            min_num = parts[1]
            max_num = parts[2]
        elif len(parts) == 2:
            max_num = parts[1]
        try:
            min_num = int(min_num)
            max_num = int(max_num)
            if int(max_num) > INTMAX_NUM:
                max_num = INTMAX_NUM
        except ValueError:
            text = "Формат: /random, /random 50, /random 50 100"
        else:
            text = generate_random(min_num=min_num, max_num=max_num)
    except ValueError:
        text = "Минимальное число должно быть меньше максимального!"
        
    bot.reply_to(message=message, text=text)

@bot.message_handler(commands=['maps'])
def cmd_maps(message: Message) -> None:
    maps = [
        "🐸Ancient",
        "🏝️Anubis",
        "🌴Dust II",
        "🌋Inferno",
        "🏜️Mirage",
        "💣Nuke",
        "🌉Overpass"
    ]

    random_map = random.choice(maps)
    bot.reply_to(message=message, text=f"Случайная карта из CS2 для рандомного поиска:\n{random_map}")

if __name__ == '__main__':
    import time
    print("Бот запущен!")
    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except Exception as error:
            print(error)
            time.sleep(5)