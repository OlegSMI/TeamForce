from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    email = State()


class FormAdmin(StatesGroup):
    photo = State()
    topic = State()
    text_topic = State()


class SenderForm(StatesGroup):
    text = State()


class MailSender(StatesGroup):
    letter = State()