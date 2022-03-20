from loguru import logger
from aiogram import Bot, types

from appbot.db import BotDB
from appbot.docs.conf import TOKEN

bot = Bot(token=TOKEN)

BotDB = BotDB('tgbase.db')

async def get_users_in_bd(msg: types.Message):
    result = BotDB.get_all_data()
    logger.debug(result)
    for i in result:
        reply_keyboard = types.InlineKeyboardMarkup()
        but_reply = types.InlineKeyboardButton(text='Ответить', callback_data=f"response:{result[i][0]}")
        but_enter = types.InlineKeyboardButton(text='Выбрать', callback_data=f"enter:{result[i][0]}")
        reply_keyboard.add(but_reply, but_enter)
        await bot.send_message(msg.chat.id, f"@{i}", reply_markup=reply_keyboard)

