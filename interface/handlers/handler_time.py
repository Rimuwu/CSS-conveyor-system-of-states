from bot.main import botik as bot, css_router
from interface.state_handlers import ChooseTimeHandler
from interface.states import GeneralStates
from aiogram.types import Message
from interface.utils import seconds_to_str, str_to_seconds

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseTime)
async def ChooseTime(message: Message):
    """Общая функция для ввода времени
    """
    number = 0

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        min_int: int = data['min_int']
        max_int: int = data['max_int']
        transmitted_data = data['transmitted_data']
        
        lang: str = data['lang']

    number = str_to_seconds(str(message.text))

    if not number and min_int != 0:
        await bot.send_message(message.chat.id, 
                "❗ Пожалуйста, введите корректное время."
                )
    elif max_int != 0 and number > max_int:
        await bot.send_message(message.chat.id, 
            f"❗ Время {seconds_to_str(number, lang)} превышает максимальное значение {seconds_to_str(max_int, lang)}"
            )
    
    elif number < min_int:
        await bot.send_message(message.chat.id, 
                f"❗ Время {seconds_to_str(number, lang)} меньше минимального значения {seconds_to_str(min_int, lang)}"
                )
    else:
        await state.clear()

        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        await ChooseTimeHandler(**data).call_function(number)
