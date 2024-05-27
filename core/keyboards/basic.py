
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard(is_admin=False):
    builder = InlineKeyboardBuilder()
    builder.button(text='Начать игру', callback_data='game')
    builder.button(text='Вопросы', callback_data='fill')
    if is_admin:
        builder.button(text='База', callback_data='show')
    builder.adjust(1, 2)
    return builder.as_markup()


def game_keyboard(num_question):
    builder = InlineKeyboardBuilder()
    builder.button(text='👍 Да', callback_data='game_yes')
    builder.button(text='👎 Нет', callback_data='game_no')

    if num_question != 0:
        builder.button(text='↩️ Предыдущий', callback_data='previous')

    builder.button(text='Пропустить', callback_data='game_skip')
    builder.button(text='🏚 В меню', callback_data='start')

    builder.adjust(2, 1 if num_question == 0 else 2, 1)
    return builder.as_markup()


def check_person_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Да', callback_data='check_person_yes')
    builder.button(text='Нет', callback_data='check_person_no')
    builder.adjust(1, 1)
    return builder.as_markup()


def fill_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить факт', callback_data='add_new_question')
    builder.button(text='📝 Выбрать факт', callback_data='fill_q')
    builder.button(text='👤 Выбрать персонажа', callback_data='fill_p')
    builder.button(text='Все случайно', callback_data='fill_start')
    builder.button(text='🏚 В меню', callback_data='start')
    builder.adjust(1, 1, 1, 1, 1)
    return builder.as_markup()


def show_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='📝 Выбрать факт', callback_data='show_q')
    builder.button(text='👤 Выбрать персонажа', callback_data='show_p')
    builder.button(text='🏚 В меню', callback_data='start')
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def fill_data_keyboard(sort_by):
    builder = InlineKeyboardBuilder()
    builder.button(text='<', callback_data='fill_left')
    builder.button(text='>', callback_data='fill_right')
    builder.button(text=f'Сортировка: по {sort_by}', callback_data='fill_sort')
    builder.button(text='Назад', callback_data='fill')
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def show_data_keyboard(sort_by):
    builder = InlineKeyboardBuilder()
    builder.button(text='<', callback_data='show_left')
    builder.button(text='>', callback_data='show_right')
    builder.button(text=f'Сортировка: по {sort_by}', callback_data='show_sort')
    builder.button(text='Назад', callback_data='show')
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def show_base_keyboard(data_type):
    builder = InlineKeyboardBuilder()
    builder.button(text='Назад', callback_data='show_' + data_type)
    builder.adjust(1)
    return builder.as_markup()


def fill_select_num_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Старт', callback_data='fill_start')
    builder.button(text='Назад', callback_data='fill')
    builder.adjust(2, 1)
    return builder.as_markup()


def fill_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='👍 Да', callback_data='fill_yes')
    builder.button(text='👎 Нет', callback_data='fill_no')
    builder.button(text='Пропустить', callback_data='fill_skip')
    builder.button(text='Назад', callback_data='fill')
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def finish_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='🏚 В меню', callback_data='start')
    builder.adjust(1, 1)
    return builder.as_markup()


def add_chance_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Да', callback_data='continue')
    builder.button(text='Хватит', callback_data='chance_no')
    builder.adjust(1, 1)
    return builder.as_markup()


def skip_photo_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Пропустить', callback_data='skip_photo')
    return builder.as_markup()


def ok_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Хорошо', callback_data='del')
    return builder.as_markup()


def new_question_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text='Назад', callback_data='fill')
    return builder.as_markup()
