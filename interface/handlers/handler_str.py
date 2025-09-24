from bot.main import botik as bot, css_router
from interface.state_handlers import ChooseStringHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseString)
async def ChooseString(message: Message):
    """Общая функция для ввода сообщения
    """

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        max_len: int = data['max_len']
        min_len: int = data['min_len']
        transmitted_data = data['transmitted_data']

        lang: str = data['lang']

    content = str(message.text)
    content_len = len(content)

    if content_len > max_len and max_len != 0:
        await bot.send_message(message.chat.id, 
                "❗ Пожалуйста, не превышайте максимальную длину сообщения. Максимальная длина: {max} символов, ваше сообщение содержит: {number} символов.".format(
                    number = content_len, max = max_len)
                )
    elif content_len < min_len:
        await bot.send_message(message.chat.id, 
                "❗ Пожалуйста, не менее {min} символов. Ваше сообщение содержит: {number} символов.".format(
                    number = content_len, min = min_len))
    else:
        await state.clear()

        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        await ChooseStringHandler(**data).call_function(content)
