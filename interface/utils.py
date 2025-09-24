import importlib
import asyncio
from typing import Union

from bot.main import botik as bot
from bot.main import STORAGE
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from interface.const import BACK_BUTTON, FORWARD_BUTTON, CANCEL_BUTTON

def get_state(user_id: int, chat_id: int):
    """ Возвращает контекст состояния для пользователя в чате
    """
    key = StorageKey(bot_id=bot.id, user_id=user_id, chat_id=chat_id)
    fsm_context = FSMContext(storage=STORAGE, key=key)
    return fsm_context


def chunks(lst: list, n: int) -> list:
    """ Делит список lst, на списки по n элементов
       Возвращает список
    """
    def work():
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    return list(work())

def filling_with_emptiness(lst: list, 
                           horizontal: int, 
                           vertical: int
                           ):
    """ Заполняет пустые элементы страницы для сохранения структуры
    """
    for i in lst:
        if len(i) != vertical:
            for _ in range(vertical - len(i)):
                i.append([' ' for _ in range(horizontal)])
    return lst

def chunk_pages(options: dict, 
                horizontal: int=2, vertical: int=3
                ):
    """ Чанкует страницы и добавляем пустые элементы для сохранения структуры
    """
    if options:
        pages = chunks(chunks(list(options.keys()), horizontal), vertical)
    else: pages = [[]]
    pages = filling_with_emptiness(pages, horizontal, vertical)
    return pages


def func_to_str(func):
    """ Преобразует функцию в строку вида 'модуль.имя_функции'.
    """
    return f"{func.__module__}.{func.__name__}"

def str_to_func(func_path):
    """ Получает функцию по строке вида 'модуль.имя_функции'.
    """

    module_name, func_name = func_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)


def list_to_keyboard(buttons: list[Union[list[str], str]], 
                     row_width: int = 3, 
                     resize_keyboard: bool = True, 
                     one_time_keyboard = None
                     ):
    """ Превращает список со списками в объект клавиатуры.
        Example:
            butttons = [ ['привет'], ['отвяжись', 'ты кто?'] ]

        >      привет
          отвяжись  ты кто?
        
            butttons = ['привет','отвяжись','ты кто?'], 
            row_width = 1

        >  привет
          отвяжись  
          ты кто?
    """
    builder = ReplyKeyboardBuilder()

    for line in buttons:
        if type(line) == list:
            builder.row(*[KeyboardButton(text=i) for i in line], width=row_width)
        else:
            builder.row(*[KeyboardButton(text=str(line))], width=row_width)

    return builder.as_markup(row_width=row_width, resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard)

def cancel_markup(
        cancel_button: str = CANCEL_BUTTON
        ) -> ReplyKeyboardMarkup:
    """Создаёт клавиатуру для отмены
    """
    return list_to_keyboard([cancel_button])

def down_menu(markup: ReplyKeyboardMarkup, 
              arrows: bool = True,
              cancel_button: str = CANCEL_BUTTON,
              back_button: str = BACK_BUTTON,
              forward_button: str = FORWARD_BUTTON,
              ): 
    """Добавления нижнего меню для страничных клавиатур
    """

    markup_n = ReplyKeyboardBuilder().from_markup(markup)

    if arrows:
        markup_n.row(*[KeyboardButton(text=i) for i in [
            back_button, cancel_button, forward_button]]
                     )
    else: 
        markup_n.row(KeyboardButton(text=cancel_button))

    return markup_n.as_markup(resize_keyboard=True)


async def async_open(file_path: str, 
                     mode: str = 'r', 
                     encoding: str = 'utf-8'
                    ):
    """ Асинхронное открытие файла.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, open, file_path, mode, encoding)

def seconds_to_time(seconds: int) -> dict:
    """ Преобразует число в словарь
    """
    time_calculation = {
        'year': 31_536_000,
        'month': 2_592_000, 'weekly': 604800,
        'day': 86400, 'hour': 3600, 
        'minute': 60, 'second': 1
    }
    time_dict = {
        'year': 0,
        'month': 0, 'weekly': 0,
        'day': 0, 'hour': 0, 
        'minute': 0, 'second': 0
    }

    for tp, unit in time_calculation.items():
        tt = seconds // unit

        if tt:
            seconds -= tt * unit
            time_dict[tp] = tt

    return time_dict 

def seconds_to_str(seconds: int, lang: str='en', mini: bool=False, max_lvl='auto'):
    """ Преобразует число секунд в строку
       Example:
       > seconds=10000 lang='ru'
       > 1 день 2 минуты 41 секунда
       
       > seconds=10000 lang='ru' mini=True
       > 1д. 2мин. 41сек.
       
       max_lvl - Определяет максимальную глубину погружения
       Example:
       > seconds=3900 max_lvl=second
       > 1ч. 5м.
       
       > seconds=3900 max_lvl=hour
       > 1ч.
    """
    if seconds == 'inf': return "♾"
    if seconds < 0: seconds = 0

    time_format = {
        'year': ['год', 'года', 'лет', 'г.'],
        'month': ['месяц', 'месяца', 'месяцев', 'мес.'],
        'weekly': ['неделя', 'недели', 'недель', 'нед.'],
        'day': ['день', 'дня', 'дней', 'д.'],
        'hour': ['час', 'часа', 'часов', 'ч.'],
        'minute': ['минута', 'минуты', 'минут', 'мин.'],
        'second': ['секунда', 'секунды', 'секунд', 'сек.']
    }
    result = ''

    def ending_w(time_type: str, unit: int) -> str:
        """Опредеяет окончание для слова
        """
        if mini: return time_format[time_type][3]

        else:
            result = ''
            if unit < 11 or unit > 14:
                unit = unit % 10

            if unit == 1:
                result = time_format[time_type][0]
            elif unit > 1 and unit <= 4:
                result = time_format[time_type][1]
            elif unit > 4 or unit == 0:
                result = time_format[time_type][2]
        return result

    data = seconds_to_time(seconds=seconds)
    if max_lvl == 'auto':
        max_lvl, a, lst_n = 'second', 0, 'second'

        for tp, unit in data.items():
            if unit: 
                a += 1
                lst_n = tp
            if a >= 3:
                max_lvl = tp
                break

        if a < 3: max_lvl = lst_n

    for tp, unit in data.items():
        if unit:
            if mini:
                result += f'{unit}{ending_w(tp, unit)} '
            else:
                result += f'{unit} {ending_w(tp, unit)} '
        if max_lvl == tp: break

    if result[:-1]: return result[:-1]
    else: 
        result = '0'
        if max_lvl != 'second': 
            return f'0 {time_format[max_lvl][3]}'
        return result


def str_to_seconds(text: str):
    """ Преобразует текст в секнудны
    """
    words = text.split()
    seconds = 0

    for i in words:
        mn = 1
        if len(i) == 1 and i.isdigit(): seconds += int(i)

        if len(i) > 1:
            if type(i[-1]) == str:
                number = i[:-1]

                if number.isdigit():
                    if i[:-1] == 's': mn = 1
                    elif i[-1] == 'm': mn = 60
                    elif i[-1] == 'h': mn = 3600
                    elif i[-1] == 'd': mn = 86400
                    elif i[-1] == 'w': mn = 86400 * 7

                    seconds += int(number) * mn
    return seconds


def list_to_inline(buttons, row_width=3):
    """ Преобразует список кнопок в inline-клавиатуру 
         Example:
              buttons = [ {'text': 'Кнопка 1', 'callback_data': 'btn1'},
                          {'text': 'Кнопка 2', 'callback_data': 'btn2'},
                          {'text': 'Кнопка 3', 'callback_data': 'btn3'} ]
              
              > Кнопка 1 | Кнопка 2 | Кнопка 3
    """

    inline_keyboard = []
    row = []
    for button in buttons:

        if 'ignore_row' in button and button['ignore_row'].lower() == 'true':
            inline_keyboard.append(row)
            row = []
            inline_keyboard.append([InlineKeyboardButton(**button)])
            continue
        row.append(InlineKeyboardButton(**button))
        if len(row) == row_width:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)