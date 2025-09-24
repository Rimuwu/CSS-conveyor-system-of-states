from bot.main import botik as bot, css_router
from interface.handlers.commands import cancel
from interface.state_handlers import ChooseConfirmHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseConfirm)
async def ChooseConfirm(message: Message):
    """Общая функция для подтверждения
    """
    content = str(message.text)

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        transmitted_data = data['transmitted_data']
        cancel_status = data['cancel']

    buttons = {
        "enable": "Включить",
        "confirm": "Подтвердить",
        "disable": "Отключить",
        "yes": "Да",
        "no": "Нет",
    }
    buttons_data = {
        buttons['enable']: True,
        buttons['confirm']: True,
        buttons['disable']: False,
        buttons['yes']: True,
        buttons['no']: False,
        'true': True,
        'false': False,
    }

    if content in buttons_data:
        if not(buttons_data[content]) and cancel_status:
            await cancel(message)
        else:
            await state.clear()

            if 'steps' in transmitted_data and 'process' in transmitted_data:
                transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
            else: transmitted_data['umessageid'] = message.message_id

            await ChooseConfirmHandler(**data).call_function(buttons_data[content])

    else:
        await bot.send_message(message.chat.id, 
                               "❗ Пожалуйста, выберите один из предложенных вариантов.")
