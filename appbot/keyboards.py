from aiogram import types

# 1
keyboard_back = types.InlineKeyboardMarkup()
back = types.InlineKeyboardButton(text='Назад', callback_data="back")
keyboard_back.add(back)

# 2
keyboard_admin = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard_admin.row('Показать все заявки')
keyboard_admin.row('Фильтр по темам')
keyboard_admin.row('Разместить новый аукцион')
keyboard_admin.row('Пригласить админа')

# 3
choicer_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
choicer_keyboard.row('Заблокировать')
choicer_keyboard.row('Сделать рассылку')
choicer_keyboard.row('Выбрать всех')
choicer_keyboard.row('Назад')

# 4
email_keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False).add("📧 Подписаться на Email Рассылку")