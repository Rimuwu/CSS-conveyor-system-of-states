from bot.main import botik as bot, css_router
from interface.state_handlers import ChooseIntHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseInt)
async def ChooseInt(message: Message):
    """Общая функция для ввода числа
    """
    number = 0

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        min_int: int = data['min_int']
        max_int: int = data['max_int']
        transmitted_data = data['transmitted_data']

    for iter_word in str(message.text).split():
        if iter_word.isdigit():
            number = int(iter_word)

    if not number and number != 0:
        await bot.send_message(message.chat.id, 
                '❗ Пожалуйста, введите число.'
                )
        
    elif max_int != 0 and number > max_int:
        await bot.send_message(message.chat.id, 
                '❗ Введённое число слишком большое. Максимально допустимое: {max}.'.format(max = max_int)
                )
    elif number < min_int:
        await bot.send_message(message.chat.id, 
                '❗ Введённое число слишком маленькое. Минимально допустимое: {min}.'.format(min = min_int)
                )
    else:
        await state.clear()

        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        await ChooseIntHandler(**data).call_function(number)