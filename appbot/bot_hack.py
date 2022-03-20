from re import M
from transliterate import translit
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from loguru import logger

from .docs.conf import TOKEN, CHANNEL_ID, ADMIN_ID
from appbot.db import BotDB
from appbot.service.filters import get_users_in_bd
from .service.states import Form, FormAdmin, SenderForm, MailSender
from .keyboards import keyboard_back, keyboard_admin, choicer_keyboard, email_keyboard
from .service.mail.smtpfile import send_message_to_email

BotDB = BotDB('tgbase.db')

globalPER = []

storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])  
async def start(msg: types.Message, state: FSMContext):
    try:
        if msg.text.split(' ')[1] == '111333':
            ADMIN_ID.append(msg.from_user.id)
            globalPER = []
            globalPER.append(msg.message_id)
            await bot.send_message(msg.chat.id, 'Вы теперь админ', reply_markup=keyboard_admin)
    except:
        pass
    if msg.chat.type == 'private':
        if msg.from_user.id in ADMIN_ID:
            logger.debug(msg.message_id)
            globalPER = []
            globalPER.append(msg.message_id)
            await bot.send_message(msg.chat.id, 'Бот запущен', reply_markup=keyboard_admin)
        else:
            if msg.from_user.id in BotDB.select_all_banned_users():
                await bot.send_message(msg.from_user.id, 'Вы забанены')
            else:
                try:
                    tops = msg.text.split(' ')[1].replace("0", "'")
                    logger.debug(tops)
                except IndexError:
                    await bot.send_message(msg.chat.id, 'Для запуска бота, выберете тему в канале: @teamforcevacansy', reply_markup=email_keyboard)
                    return
                if(not BotDB.user_exists(msg.from_user.id)):
                    tops = translit(tops, 'ru').replace('_', ' ')
                    BotDB.add_user(msg.from_user.id, msg.from_user.username)
                    BotDB.add_topic(tops, msg.from_user.id)
                    logger.debug('Добавлен пользователь: {}'.format(msg.from_user.id))
                    await bot.send_message(msg.chat.id, f'Добрый день, тема вашего аукциона: {tops}', reply_markup=email_keyboard)
                    async with state.proxy() as data:
                        data['topic'] = tops  
                else:
                    topics = BotDB.topic_exists(msg.from_user.id) 
                    if any([top == tops for top in topics]):
                        await bot.send_message(msg.chat.id, f'Добрый день, тема вашего аукциона: {tops}', reply_markup=email_keyboard)
                        reply_keyboard = types.InlineKeyboardMarkup()
                        but_reply = types.InlineKeyboardButton(text='Ответить', callback_data=f"response:{msg.from_user.id}")
                        but_enter = types.InlineKeyboardButton(text='Выбрать', callback_data=f"enter:{msg.from_user.id}")
                        reply_keyboard.add(but_reply, but_enter)
                        await bot.send_message(ADMIN_ID[0], f'@{msg.from_user.username}', reply_markup=reply_keyboard)
                    else:
                        await bot.send_message(msg.chat.id, f'Добрый день, тема вашего аукциона: {tops}', reply_markup=email_keyboard)
                        tops = translit(tops, 'ru').replace('_', ' ')
                        logger.debug(f"добавлена тема {tops}")
                        BotDB.add_topic(tops, msg.from_user.id)
            

#часть админа

@dp.message_handler(lambda message: message.text == "Разместить новый аукцион")
async def post_topic(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    await FormAdmin.photo.set()
    await bot.send_message(msg.chat.id, 'Добавьте фото аукциона: ', reply_markup=keyboard_back)  


@dp.message_handler(state=FormAdmin.photo, content_types=["photo"])
async def send_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data_admin:
        data_admin['photo'] = msg.photo[-1].file_id
    await FormAdmin.next()
    await msg.reply('Введите название темы аукциона: ', reply_markup=keyboard_back)

@dp.message_handler(state=FormAdmin.topic)   
async def post_vacancy(msg: types.Message, state: FSMContext):
    async with state.proxy() as data_admin:
        data_admin['topic'] = msg.text
    await FormAdmin.next()
    await msg.reply('Введите текст аукциона: ', reply_markup=keyboard_back)


@dp.message_handler(state=FormAdmin.text_topic)   
async def post_vacancy(msg: types.Message, state: FSMContext):
    async with state.proxy() as data_admin:
        data_admin['text_topic'] = msg.text
    await state.finish()
    text_vacancy = f"Новый аукцион:\n\nТема: {data_admin['topic']}\n\nТекст: {data_admin['text_topic']}"
    for i in BotDB.all_emails():
        try:
            await send_message_to_email(i, f"{data_admin['photo']} {text_vacancy}")
        except:
            pass
    keybord_vacancy = types.InlineKeyboardMarkup()
    themm = translit(data_admin['topic'], 'ru', reversed=True).replace(' ', '_').replace("'", "0") 
    but_link = types.InlineKeyboardButton(text="Выбрать аукцион", url=f"https://t.me/TeamForceChatBot?start={themm}" )
    keybord_vacancy.add(but_link)
    await bot.send_photo(CHANNEL_ID, data_admin['photo'], caption=text_vacancy,reply_markup=keybord_vacancy)
    await bot.send_message(msg.from_user.id, 'Успешно', reply_markup=keyboard_admin)


@dp.callback_query_handler(text="back", state=FormAdmin)
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await call.message.answer('Выберете действие: ', reply_markup=keyboard_admin) 


@dp.message_handler(lambda message: message.text == "Фильтр по темам")
async def filter_topics(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    topics = BotDB.filter_topic()
    keybords_topics = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in set(topics):
        keybords_topics.row(i)
    keybords_topics.row('Назад')
    await bot.send_message(msg.chat.id, 'Фильтр по темам: ', reply_markup=keybords_topics)


@dp.message_handler(lambda message: message.text in set(BotDB.filter_topic()))
async def get_users_for_topic(msg: types.Message):
    await get_users_in_bd(msg)
    await bot.send_message(msg.from_user.id, 'Выбрать действие', reply_markup=keyboard_admin)


@dp.message_handler(lambda message: message.text == "Показать все заявки")
async def show_all_themes(msg: types.Message):    
    if msg.from_user.id not in ADMIN_ID:
        return
    await get_users_in_bd(msg)
    await bot.send_message(msg.from_user.id, 'Выбрать действие', reply_markup=keyboard_admin)

#часть юзера

@dp.message_handler(lambda message: message.from_user.id in BotDB.select_all_banned_users())
async def handle_banned(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Вы забанены')
    return True

# часть админа снова

@dp.callback_query_handler(text_contains="response")
async def response_handler(call: types.CallbackQuery, state: FSMContext):
    logger.debug(call.data)
    user_id = call.data.split(':')[1]
    if call.from_user.id not in ADMIN_ID:
        return
    async with state.proxy() as data_email:
        data_email['user_id'] = user_id
    await call.message.answer('Напишите ответ: ')    
    await MailSender.letter.set()
    

@dp.message_handler(state=MailSender.letter)  
async def get_mess_in_bd(msg: types.Message, state: FSMContext):
    async with state.proxy() as data_email:
        data_email['text'] = msg.text
        data_email['message'] = msg.message_id
    await state.finish()
    await bot.send_message(data_email['user_id'], data_email['text'], reply_markup=email_keyboard)


@dp.callback_query_handler(text_contains="enter")
async def enter_handler(call: types.CallbackQuery, state: FSMContext):
    person = call.data.split(':')[1]
    msg_id = globalPER[0]
    logger.debug(msg_id)
    BotDB.add_chois_user(person)
    await call.message.answer('Действие с выбранными пользователями:', reply_markup=choicer_keyboard)
    await bot.edit_message_text("result", chat_id=person, message_id=msg_id)
    await bot.delete_message(person, msg_id)

@dp.message_handler(lambda message: message.text == "Выбрать всех")
async def create_group_topic(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    # указанная тема
    # choices_users = из бд
    keyboard_choice_all = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add('Сделать рассылку', 'Назад')
    await bot.send_message(msg.from_user.id, 'Введите действие: ', reply_markup=keyboard_choice_all)


@dp.message_handler(lambda message: message.text == "Пригласить админа")
async def folllow_admin(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    keyboard_add_admin = types.InlineKeyboardMarkup()
    but = types.InlineKeyboardButton(text='Поделиться', switch_inline_query="\n\nhttps://t.me/TeamForceChatBot?start=111333")
    keyboard_add_admin.add(but)
    await bot.send_message(msg.from_user.id, 'Вот ваша ссылка', reply_markup=keyboard_add_admin)


@dp.message_handler(lambda message: message.text == "Сделать рассылку")
async def create_group_topic(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    await SenderForm.text.set()
    await bot.send_message(msg.chat.id, 'Введите текс рассылки: ')


@dp.message_handler(state=SenderForm.text)
async def create_group_topic(msg: types.Message, state: FSMContext): 
    async with state.proxy() as data:
        data['text'] = msg.text
    await state.finish()
    user_data = BotDB.select_all_choices_users() 
    for i in user_data:
        await bot.send_message(i, data['text'])
    BotDB.clean_table_choices_users()


@dp.message_handler(lambda message: message.text == "Заблокировать")
async def create_group_topic(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return
    for user_id in BotDB.select_all_choices_users():
        BotDB.add_banned_user(user_id)
        logger.debug(f"Пользователь {user_id} заблокирован.")
    BotDB.clean_table_choices_users()


@dp.message_handler(lambda message: message.text == "Назад")
async def create_group_topic(msg: types.Message):
    if msg.from_user.id not in ADMIN_ID:
        return  
    await bot.send_message(msg.chat.id, 'Выберете действия: ', reply_markup=keyboard_admin)


#часть юзера снова

@dp.message_handler(lambda message: message.text == "📧 Подписаться на Email Рассылку")
async def post_topic(msg: types.Message): 
    if msg.from_user.id in ADMIN_ID:
        return
    await Form.email.set()
    await bot.send_message(msg.from_user.id, 'Ввведите ваш Email: ')


@dp.message_handler(state=Form.email)
async def post_topic(msg: types.Message, state: FSMContext): 
    async with state.proxy() as data_em_bd:
        data_em_bd['email'] = msg.text
    await state.finish()
    if msg.text in BotDB.all_emails():
        await bot.send_message(msg.from_user.id, 'Вы уже подписаны')
    else:
        BotDB.add_email(msg.text)
        await bot.send_message(msg.from_user.id, 'Вы подписались на рассылку🎉')
    
    

@dp.message_handler()
async def post_topic(msg: types.Message):   
    if msg.from_user.id in ADMIN_ID:
        return
    if msg.text != '/start':
        reply_keyboard = types.InlineKeyboardMarkup()
        but_reply = types.InlineKeyboardButton(text='Ответить', callback_data=f"response:{msg.from_user.id}")
        but_enter = types.InlineKeyboardButton(text='Выбрать', callback_data=f"enter:{msg.from_user.id}")
        reply_keyboard.add(but_reply, but_enter)
        await bot.send_message(ADMIN_ID[0], f'Пользователь @{msg.from_user.username}: {msg.text}', reply_markup=reply_keyboard)
        

 
def run_polling():
    executor.start_polling(dp, skip_updates=True)