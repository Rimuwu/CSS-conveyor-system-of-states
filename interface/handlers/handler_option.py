from bot.main import botik as bot, css_router
from interface.state_handlers import ChooseOptionHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseOption)
async def ChooseOption(message: Message):
    """Общая функция для выбора из предложенных вариантов
    """

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        options: dict = data['options']
        transmitted_data = data['transmitted_data']

    if message.text in options.keys():
        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        await state.clear()
        await ChooseOptionHandler(**data).call_function(options[message.text])
    else:
        await bot.send_message(message.chat.id, 
                    "❗ Пожалуйста, выберите один из предложенных вариантов."
                )
