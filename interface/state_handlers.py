import inspect
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, Message
from bson import Binary, Code, Decimal128, Int64, MaxKey, MinKey, ObjectId, Regex, Timestamp

from bot.main import botik as bot
from interface.steps_datatype import (
    BaseDataType, BaseUpdateType, DataType, InlineStepData, StepMessage, get_step_data
)
from interface.states import GeneralStates
from interface.utils import chunk_pages, list_to_keyboard, down_menu, get_state, func_to_str, str_to_func, async_open


states_to_str: dict[str, State] = {}

BaseValueType = Union[
    str,
    int,
    float,
    bool,
    None,
    Dict[str, Any],
    List[Any],
    ObjectId,
    bytes,
    Binary,
    Code,
    Decimal128,
    Int64,
    MaxKey,
    MinKey,
    Regex,
    Timestamp,
]

StatesGroups: List[Type[StatesGroup]] = [
    GeneralStates
]

def get_state_names() -> dict:
    """ Получение всех состояний из всех групп состояний.
    """
    states_to_str = {}
    for state_group in StatesGroups:
        for state_name, state in state_group.__dict__.items():
            if isinstance(state, State):
                states_to_str[f"{state_group.__name__}:{state_name}"] = state

    return states_to_str

def get_state_functions_names() -> dict:
    """ Получение всех обработчиков состояний выбора.
    """
    state_functions_to_str = {}
    for subclass in BaseStateHandler.__subclasses__():
        state_functions_to_str[
            subclass.group_name.__name__ + ':' + subclass.state_name
        ] = subclass

    return state_functions_to_str


class BaseStateHandler():
    """
    Абстрактный базовый класс для обработчиков состояний выбора.
    """
    group_name = GeneralStates
    state_name = 'zero'
    indenf: str = 'zero'
    deleted_keys: list[str] = ['message']

    def setState(self):
        """
        Получение состояния из группы состояний и установка его в качестве типового состояния.
        """

        return getattr(self.group_name, self.state_name, None)

    def __init__(self, function: Callable | str, 
                 userid: int, chatid: int, lang: str, 
                 transmitted_data: Optional[dict[str, BaseValueType]] = None,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                #  end_process: bool = True
                 ):
        if isinstance(function, str):
            self.function = function
        elif callable(function):
            self.function = func_to_str(function)
        else:
            raise TypeError("Функция должна быть строкой или вызываемым объектом.")

        self.userid: int = userid
        self.chatid: int = chatid
        self.lang: str = lang
        self.transmitted_data = transmitted_data or {}

        self.state_type = self.setState()
        self.message: Optional[StepMessage] = message
        self.messages_list: list[int] = messages_list or []
        # self.end_process: bool = end_process

    async def pre_data(self, value: Any) -> Any:
        """
        Предварительная обработка данных перед вызовом функции.
        """
        # Здесь можно добавить логику предварительной обработки данных, если необходимо.
        return value

    async def call_function(self, value: Any):
        value = await self.pre_data(value)
        func = str_to_func(self.function)

        transmitted_data = self.transmitted_data.copy()
        transmitted_data.update(
            {
                'userid': self.userid,
                'chatid': self.chatid,
                'lang': self.lang,
                'messages_list': self.messages_list # Список с id всех отправленных в состоянии сообщений
            }
        )

        if inspect.iscoroutinefunction(func):
            return await func(value, 
                              transmitted_data=transmitted_data)
        else:
            return func(value, 
                        transmitted_data=transmitted_data)

    async def setup(self) -> tuple[bool, str]:
        """
        Настройка состояния. Должна быть переопределена в дочерних классах.
        """
        raise NotImplementedError("Метод setup должен быть переопределен в дочернем классе.")

    async def message_sender(self) -> None:
        """
        Отправка сообщения пользователю.
        """

        if isinstance(self.message, StepMessage):
            text = self.message.get_text(self.lang)
            markup = self.message.markup
            parse_mode = self.message.parse_mode
            image = self.message.image

            if image:
                photo = await async_open(image, True)
                res = await bot.send_photo(self.chatid, 
                        photo, caption=text, 
                        parse_mode=parse_mode, reply_markup=markup)
            else:
                res = await bot.send_message(self.chatid, 
                        text, parse_mode=parse_mode, 
                        reply_markup=markup)
            self.messages_list.append(res.message_id)

        return

    async def start(self) -> tuple[bool, str]:
        """
        Запуск состояния. 
        Делаем стандартные действия и вызывает setup()
        """
        user_state = get_state(self.userid, self.chatid)

        await user_state.clear()
        res = await self.setup()
        await self.message_sender()
        return res

    async def set_data(self) -> None:
        state = get_state(self.userid, self.chatid)

        data = self.get_data()
        await state.set_data(data)

    def get_data(self) -> dict:
        data = self.__dict__.copy()

        del data['state_type']
        for i in self.deleted_keys: del data[i]

        if 'time_start' not in data:
            data['time_start'] = int(time.time())

        return data

    async def set_state(self):
        user_state = get_state(self.userid, self.chatid)
        await user_state.set_state(self.state_type)
        return user_state

class ChooseIntHandler(BaseStateHandler):
    state_name =  'ChooseInt'
    indenf = 'int'
    deleted_keys = ['autoanswer', 'message']

    def __init__(self, function, userid, chatid, lang, 
                 min_int=1, max_int=10, autoanswer=True, 
                 transmitted_data:Optional[dict[str, BaseValueType]]=None,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """
            Устанавливает состояние ожидания числа

            В function передаёт 
            >>> number: int, transmitted_data: dict
            
            Если max_int == 0, значит нет ограничения.

            >>> return: Возвращает True если был создано состояние, False если завершилось автоматически (минимальный и максимальный вариант совпадают)
        """

        super().__init__(function, userid, chatid, lang, transmitted_data, 
                         message=message, messages_list=messages_list)
        self.min_int = min_int
        self.max_int = max_int
        self.autoanswer = autoanswer

    async def setup(self) -> tuple[bool, str]:

        if self.min_int != self.max_int or not self.autoanswer:
           await self.set_state()
           await self.set_data()
           return True, self.indenf

        else:
            await self.call_function(self.min_int)
            return False, self.indenf

class ChooseStringHandler(BaseStateHandler):
    state_name =  'ChooseString'
    indenf = 'string'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang, 
                 min_len=1, max_len=10, 
                 transmitted_data:Optional[dict[str, BaseValueType]]=None,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания сообщения

            В function передаёт 
            >>> string: str, transmitted_data: dict
            
            Return:
            Возвращает True если был создано состояние, не может завершится автоматически
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        self.min_len = min_len
        self.max_len = max_len

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf

class ChooseTimeHandler(BaseStateHandler):
    state_name = 'ChooseTime'
    indenf = 'time'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang,
                 min_int=1, max_int=10, 
                 transmitted_data:Optional[dict[str, BaseValueType]]=None, 
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания сообщения в формате времени

            В function передаёт 
            >>> string: str, transmitted_data: dict
            
            Return:
            Возвращает True если был создано состояние, не может завершится автоматически
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        self.min_int = min_int
        self.max_int = max_int

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf

class ChooseConfirmHandler(BaseStateHandler):
    state_name = 'ChooseConfirm'
    indenf = 'confirm'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang, 
                 cancel=False, transmitted_data:Optional[dict[str, BaseValueType]]=None, 
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания подтверждения действия

            В function передаёт 
            >>> answer: bool, transmitted_data: dict

            cancel - если True, то при отказе вызывает возврат в меню

            Return:
            Возвращает True если был создано состояние, не может завершится автоматически
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        self.cancel = cancel

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf

class ChooseOptionHandler(BaseStateHandler):
    state_name = 'ChooseOption'
    indenf = 'option'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang, 
                 options: Optional[dict] = None, 
                 transmitted_data:Optional[dict[str, BaseValueType]]=None,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания выбора опции

            В function передаёт 
            >>> answer: ???, transmitted_data: dict

            options - {"кнопка": данные}

            Return:
            Возвращает True если был создано состояние, False если завершилось автоматически (1 вариант выбора)
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        if options is None: 
            self.options = {}
        else: self.options = options

    async def setup(self):
        if len(self.options) > 1:
            await self.set_state()
            await self.set_data()
            return True, self.indenf

        else:
            element = None
            if len(self.options.keys()) > 0:
                element = self.options[list(self.options.keys())[0]]
            await self.call_function(element)
            return False, self.indenf

class ChooseInlineHandler(BaseStateHandler):
    state_name = 'ChooseInline'
    indenf = 'inline'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang, 
                 custom_code: str, 
                 transmitted_data: Optional[dict[str, BaseValueType]] = None,
                 one_element: bool = True,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания нажатия кнопки
            Все ключи callback должны начинаться с 'chooseinline'
            custom_code - код сессии запроса кнопок (индекс 1)

            В function передаёт 
            >>> answer: list, transmitted_data: dict
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        self.custom_code: str = custom_code
        self.one_element: bool = one_element

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf

class ChooseCustomHandler(BaseStateHandler):
    state_name = 'ChooseCustom'
    indenf = 'custom'
    deleted_keys = ['message']

    def __init__(self, function, 
                 custom_handler, userid, 
                 chatid, lang, 
                 transmitted_data:Optional[dict[str, BaseValueType]]=None,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """
            Устанавливает состояние ожидания чего-либо, все проверки идут через custom_handler.

            custom_handler -> bool, Any !
            В custom_handler передаётся (Message, transmitted_data)

            В function передаёт:
            >>> answer: ???, transmitted_data: dict

            Return:
                result - второе возвращаемое из custom_handler
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)

        if isinstance(custom_handler, str):
            self.custom_handler = custom_handler
        elif callable(custom_handler):
            self.custom_handler = func_to_str(custom_handler)

    async def call_custom_handler(self, message: Message) -> tuple[bool, Any]:
        func = str_to_func(self.custom_handler)

        transmitted_data = self.transmitted_data.copy()
        transmitted_data.update(
            {
                'userid': self.userid,
                'chatid': self.chatid,
                'lang': self.lang
            }
        )

        if inspect.iscoroutinefunction(func):
            return await func(message, transmitted_data=transmitted_data)
        else:
            return func(message, transmitted_data=transmitted_data)

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf


async def update_page(pages: list, 
                      page: int, 
                      chat_id: int, 
                      lang: str,
                      upd_text: str = '🔁 | Страница обновлена'
                      ):
    """
        Стандартная функция обновления страницы, которая будет передаваться в состояние выбора страниц.
    """

    keyboard = list_to_keyboard(pages[page])
    keyboard = down_menu(keyboard, len(pages) > 1, lang)

    return await bot.send_message(chat_id, 
                                  upd_text, 
                                  reply_markup=keyboard)

class ChoosePagesStateHandler(BaseStateHandler):
    state_name = 'ChoosePagesState'
    indenf = 'pages'
    deleted_keys = ['autoanswer', 'message']

    def __init__(self, function, userid, 
                 chatid, lang,
                 options=None, 
                 horizontal=2, vertical=3,
                 transmitted_data:Optional[dict[str, BaseValueType]]=None, 
                 autoanswer=True, one_element=True, 
                 settings: Optional[dict]=None,
                 update_page_function: Optional[Callable]=None,
                 pages: Optional[list] = None,
                 page: int = 0,
                 message: Optional[StepMessage] = None,
                 messages_list: Optional[List[int]] = None,
                 **kwargs):
        """ Устанавливает состояние ожидания выбора опции
    
            options = {
                'button_name': data
            }

            autoanswer - надо ли делать авто ответ, при 1-ом варианте
            horizontal, vertical - размер страницы
            one_element - будет ли завершаться работа после выбора одного элемента

            В function передаёт 
            >>> answer: ???, transmitted_data: dict
                return 
                - если не требуется ничего обновлять, можно ничего не возвращать.
                - если требуется после какого то элемента удалить состояние - {'status': 'reset'}
                - если требуется обновить страницу с переданными данными - {'status': 'update', 'options': {}} (по желанию ключ 'page')
                - если требуется удалить или добавить элемент, при этом обновив страницу 
                {'status': 'edit', 'elements': {'add' | 'delete': data}}
                    - 'add' - в data требуется передать словарь с ключами, данные объединяются
                    - 'delete' - в data требуется передать список с ключами, ключи будут удалены

            В update_page_function передаёт 
            >>> pages: list, page: int, chat_id: int, lang: str

            Return:
            Возвращает True если был создано состояние, False если завершилось автоматически (1 вариант выбора)
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)

        self.options: dict = options or {}
        self.autoanswer: bool = autoanswer
        self.one_element: bool = one_element

        if update_page_function is None:
            self.update_page_function = func_to_str(update_page)
        elif isinstance(update_page_function, str):
            self.update_page_function = update_page_function
        elif callable(update_page_function):
            self.update_page_function = func_to_str(update_page_function)

        self.pages: list = pages or []
        self.page: int = page
        self.settings: dict = {
            'horizontal': horizontal,
            'vertical': vertical
        }

        if settings:
            self.settings.update(settings)

    async def call_update_page_function(self, pages: 
        list, page: int, chatid: int, lang: str):
        func = str_to_func(self.update_page_function)

        if inspect.iscoroutinefunction(func):
            return await func(pages, page, chatid, lang)
        else:
            return func(pages, page, chatid, lang)

    async def setup(self):
        # Чанкует страницы и добавляем пустые элементы для сохранения структуры
        self.pages = chunk_pages(self.options, 
                                 self.settings['horizontal'], self.settings['vertical'])

        if len(self.options) > 1 or not self.autoanswer:
            await self.set_state()
            await self.set_data()

            await self.call_update_page_function(self.pages, 
                                self.page, self.chatid, self.lang)
            return True, self.pages
        else:
            if len(self.options) == 0:
                element = None
            else:
                element = self.options[list(self.options.keys())[0]]
            await self.call_function(element)
            return False, self.pages

class ChooseImageHandler(BaseStateHandler):
    state_name = 'ChooseImage'
    indenf = 'image'
    deleted_keys = ['message']

    def __init__(self, function, userid, chatid, lang,
                    need_image=True, 
                    transmitted_data:Optional[dict[str, BaseValueType]]=None,
                    message: Optional[StepMessage] = None,
                    messages_list: Optional[List[int]] = None,
                    **kwargs):
        """
            Устанавливает состояние ожидания ввода изображения

            need_image - если True, разрешает ответ 'no_image' вместо file_id

            В function передаёт:
            >>> image_url: str, transmitted_data: dict

            Return:
                True, 'image'
        """
        super().__init__(function, userid, chatid, lang, transmitted_data,
                         message=message, messages_list=messages_list)
        self.need_image = need_image

    async def setup(self):
        await self.set_state()
        await self.set_data()
        return True, self.indenf

class BaseUpdateHandler():

    def __init__(self, function: Callable | str, 
                 transmitted_data: Optional[dict] = None,
                 ):

        if isinstance(function, str):
            self.function = function
        elif callable(function):
            self.function = func_to_str(function)

        self.transmitted_data: dict = transmitted_data or {}

    async def start(self) -> tuple[dict[str, Any], bool]:
        func = str_to_func(self.function)

        if inspect.iscoroutinefunction(func):
            return await func(self.transmitted_data)
        else:
            return func(self.transmitted_data)

    async def get_data(self) -> dict[str, Any]:
        return self.__dict__

# Пример реестра классов-состояний
state_handler_registry: Dict[str, Type[BaseStateHandler]] = {
    'int': ChooseIntHandler,
    'time': ChooseTimeHandler,
    'str': ChooseStringHandler,
    'bool': ChooseConfirmHandler,
    'option': ChooseOptionHandler,
    'inline': ChooseInlineHandler,
    'custom': ChooseCustomHandler,
    'pages': ChoosePagesStateHandler,
    'image': ChooseImageHandler,
}

# Пример функции для запуска состояния по типу
async def run_state_handler(state_type: str, *args, **kwargs):
    handler_cls = state_handler_registry.get(state_type)
    if not handler_cls:
        raise ValueError(f"State handler for type '{state_type}' not found.")
    handler = handler_cls(*args, **kwargs)
    return await handler.setup()

class ChooseStepHandler():

    def __init__(self, function: Callable | str, 
                 userid: int, chatid: int, 
                 lang: str, 
                 steps: list[DataType],
                 transmitted_data:Optional[dict[str, BaseValueType]] = None):
        """ Конвейерная Система Состояний (КСС)
            Устанавливает ожидание нескольких ответов, запуская состояния по очереди.

            steps = [
                DinoStepData('step_name', # тут лежит type состояния
                    None,
                    data={
                        'add_egg': True, 'all_dinos': True,
                    }
                ),
                IntStepData('step_name_int',
                    StepMessage('text_int', markup_int), # отсюда получается текст через get_text
                    data={
                        'min_value': 0, 'max_value': 100,
                    }
                ),
            ]
            type - тип опроса пользователя (BaseDataType)
            или BaseUpdateType c функцией для обновления данных 
            (получает и возвращает transmitted_data) + возвращает ответ для сохранения

            Функция автоматически вызывается асинхронно, если она не является корутиной.

            Возвращает:
                name - имя ключа в возвращаемом инвентаре (при повторении, будет создан список с записями)

            data - данные для функции создания опроса
            message - данные для отправляемо сообщения перед опросом
            translate_message (bool, optional) - если наш текст это чистый ключ из данных, то можно переводить на ходу
                translate_args - словарь с аргументами для перевода
            image (str, optional) - если нам надо отправить картинку, то добавляем сюда путь к ней

            ТОЛЬКО ДЛЯ Inline
            delete_markup  (bool, optional) - удаляет клавиатуру после завершения

            delete_user_message (boll, optional) - удалить сообщение пользователя на следующем этапе
            delete_message (boll, optional) - удалить сообщения бота на следующем этапе

            transmitted_data
            edit_message (bool, optional) - если нужно не отсылать сообщения, а обновлять, то можно добавить этот ключ.
            delete_steps (bool, optional) - можно добавить для удаления данных отработанных шагов

            В function передаёт 
            >>> answer: dict, transmitted_data: dict
        """
        self.transmitted_data: dict = transmitted_data or {}
        for key, value in self.transmitted_data.items():
            if not isinstance(value, (str, int, float, bool, type(None), dict, list, ObjectId, bytes, Binary, Code, Decimal128, Int64, MaxKey, MinKey, Regex, Timestamp)):
                raise TypeError(f"Value for key '{key}' is not a valid BaseValueType: {type(value)}")

        for i in steps:
            if not isinstance(i, DataType):
                raise TypeError("Шаги должны быть наследниками BaseDataType")

        self.steps = steps

        if isinstance(function, str):
            self.function = function
        elif callable(function):
            self.function = func_to_str(function)
        else:
            raise TypeError("Функция должна быть строкой или вызываемым объектом.")

        self.userid: int = userid
        self.chatid: int = chatid
        self.lang: str = lang

    async def start(self) -> None:
        steps_data = []
        for step in self.steps:
            steps_data.append(
                step.to_dict()
            )

        self.transmitted_data.update(
            {
                'userid': self.userid,
                'chatid': self.chatid,
                'lang': self.lang,
                'return_function': self.function,
                'steps': steps_data,
                'process': 0,
                'return_data': {}
            }
        )

        await next_step(0, self.transmitted_data, start=True)


async def exit_chose(state, transmitted_data: dict):
    await state.clear()

    return_function: str = transmitted_data['return_function']
    return_data = transmitted_data['return_data']
    for i in ['return_function', 'return_data', 'process']:
        del transmitted_data[i]

    call_func = str_to_func(return_function)
    if inspect.iscoroutinefunction(call_func):
        await call_func(return_data, transmitted_data)
    else:
        call_func(return_data, transmitted_data)

async def next_step(answer: Any, 
                    transmitted_data: dict, 
                    start: bool = False):
    """Обработчик КСС*

    Args:
        answer (_type_): Ответ переданный из функции ожидания
        transmitted_data (dict): Переданная дата
        start (bool, optional): Является ли функция стартом КСС Defaults to False.

        Для фото, добавить в message ключ image с путём до фото

        Для edit_message требуется добавление message_data в transmitted_data.temp
        (Использовать только для inline состояний, не подойдёт для MessageSteps)
    """

    userid = transmitted_data['userid']
    chatid = transmitted_data['chatid']
    lang = transmitted_data['lang']
    steps_raw = transmitted_data['steps']
    process = transmitted_data['process']
    return_data = transmitted_data['return_data']

    user_state = get_state(userid, chatid)
    temp = {}

    # Преобразование в дата классы для удобной работы
    steps: list[Union[Type[BaseDataType], BaseUpdateType]] = []
    for raw_step in steps_raw.copy():
        if raw_step['type'] in state_handler_registry.keys():
            step = get_step_data(**raw_step)
        else:
            new_step: dict = raw_step.copy()
            new_step.pop('type', None)
            step = BaseUpdateType(**new_step)

        steps.append(step)

    current_step: Union[Type[BaseDataType], BaseUpdateType] = steps[process]

    # Обновление внутренних данных
    if not start:

        # Обновляем данные в return_data если есть имя
        if isinstance(current_step, (BaseDataType)):
            name = current_step.name
            if name:
                # Добавление данных в return_data
                if name in return_data:
                    if isinstance(return_data[name], list):
                        return_data[name].append(answer)
                    else:
                        return_data[name] = [
                            return_data[name], answer
                            ]
                else: 
                    return_data[name] = answer
        process += 1

    # Выполнение работы для последнего выполненного шага
    if process - 1 >= 0:
        last_step: Union[Type[BaseDataType], BaseUpdateType] = steps[process - 1]
        raw_dat = steps_raw[process - 1]

        if isinstance(last_step, InlineStepData):
            if last_step.delete_markup:
                messageid = raw_dat.get('messageid', None)
                if messageid:
                    await bot.edit_message_reply_markup(None, chatid, 
                            messageid, 
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))

            if last_step.delete_message:
                messageid = raw_dat.get('bmessageid', None)
                if messageid:
                    await bot.delete_message(chatid, messageid)

            if last_step.delete_user_message:
                messageid = raw_dat.get('umessageid', None)
                if messageid:
                    await bot.delete_message(chatid, messageid)

    # Работа с новым шагом
    if process < len(steps):
        next_step_obj: DataType = steps[process]
        step_data = next_step_obj.to_handler_data()

        if isinstance(next_step_obj, BaseUpdateType):
            # Обновление данных между запросами
            transmitted_data['process'] = process
            transmitted_data['return_data'] = return_data
            handler = BaseUpdateHandler

            self_handler = handler(**step_data, transmitted_data=transmitted_data)
            transmitted_data, answer = await self_handler.start() # Передаём transmitted_data,
            # Получаем transmitted_data и ответ для сохранения

            process = transmitted_data['process']

            new_steps: list[dict] = []
            for raw_step in transmitted_data['steps'].copy():
                if not isinstance(raw_step, dict):
                    new_steps.append(raw_step.to_dict())
                else:
                    new_steps.append(raw_step)

            transmitted_data['steps'] = new_steps

            if process >= len(steps):
                # Если это последний шаг, то удаляем состояние и завершаем работу
                await exit_chose(user_state, transmitted_data)
                return

            await user_state.update_data(transmitted_data=transmitted_data)
            await next_step(answer, transmitted_data)
            return

        if transmitted_data.get('temp', False):
            # Если это inline состояние, то обновляем сообщение
            temp = transmitted_data['temp'].copy()
            del transmitted_data['temp']

        if isinstance(next_step_obj, (BaseDataType)):
            # Запуск следующего состояния
            type_handler = next_step_obj.type
            handler = state_handler_registry[type_handler]

            transmitted_data['process'] = process
            transmitted_data['return_data'] = return_data

            self_handler = handler(**step_data, userid=userid, chatid=chatid, 
                                   lang=lang, function=next_step, transmitted_data=transmitted_data)

            func_answer, func_type = await self_handler.start()

            # Если состояние завершилось автоматически, то удаляем состояние
            if func_type == 'cancel': await user_state.clear()

            if func_answer:
                # Отправка сообщения / фото из image, если None - ничего
                edit_message, last_message = False, None
                bmessage = None
                message_data = next_step_obj.message

                if 'edit_message' in transmitted_data:
                    edit_message = transmitted_data['edit_message']

                if 'message_data' in temp:
                    last_message = temp['message_data']

                if message_data:
                    step_0: (BaseDataType) = steps[0] # type: ignore
                    if edit_message and last_message:
                        if step_0.message and step_0.message.image:
                            markup = None

                            if isinstance(message_data.markup, InlineKeyboardMarkup):
                                markup = message_data.markup

                            await bot.edit_message_caption(
                                chat_id=chatid, message_id=last_message.message_id,
                                parse_mode='Markdown', 
                                caption=message_data.get_text(lang),
                                reply_markup=markup,
                                )
 
                        if step_0.message and not step_0.message.image:

                            markup = None
                            if isinstance(message_data.markup, InlineKeyboardMarkup):
                                markup = message_data.markup

                            await bot.edit_message_text(text=message_data.get_text(lang), 
                                chat_id=chatid, message_id=last_message.message_id,
                                parse_mode='Markdown', 
                                reply_markup=markup,
                                )

                        bmessage = last_message

                    else:
                        if message_data.image:
                            photo = await async_open(message_data.image, True)
                            bmessage = await bot.send_photo(chatid, 
                                photo=photo, parse_mode='Markdown', 
                                caption=message_data.get_text(lang),
                                reply_markup=message_data.markup,
                            )
                        else:
                            try:
                                bmessage = await bot.send_message(chatid, 
                                        parse_mode='Markdown', text=message_data.get_text(lang), reply_markup=message_data.markup)
                            except:
                                bmessage = await bot.send_message(chatid,          
                                        text=message_data.get_text(lang), reply_markup=message_data.markup)

                if bmessage:
                    steps_raw[process]['bmessageid'] = bmessage.message_id

            # Обновление данных состояния
            if not start and func_answer:
                transmitted_data['steps'] = steps_raw
                await user_state.update_data(transmitted_data=transmitted_data)

    else:
        await exit_chose(user_state, transmitted_data)


# Словарь хранения состояний
states_to_str: dict[str, State] = get_state_names()

# Словарь хранения функций запуска состояний
state_functions_to_str: dict[str, Type[BaseStateHandler]] = get_state_functions_names()