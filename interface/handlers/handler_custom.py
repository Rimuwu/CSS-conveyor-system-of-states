from bot.main import css_router
from interface.state_handlers import ChooseCustomHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(GeneralStates.ChooseCustom)
async def ChooseCustom(message: Message):
    """Кастомный обработчик, принимает данные и отправляет в обработчик
    """

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        transmitted_data = data['transmitted_data']

    handler = ChooseCustomHandler(**data)

    result, answer = await handler.call_custom_handler(message) # Обязан возвращать bool, Any

    if result:
        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        await state.clear()
        await ChooseCustomHandler(**data).call_function(answer)
