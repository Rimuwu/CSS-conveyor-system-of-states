from aiogram import F
from bot.main import css_router
from interface.handlers.commands import cancel
from interface.state_handlers import ChooseConfirmHandler, ChooseInlineHandler
from interface.states import GeneralStates
from aiogram.types import CallbackQuery

from interface.utils import get_state

@css_router.callback_query(GeneralStates.ChooseInline, F.data.startswith('chooseinline'))
async def ChooseInline(callback: CallbackQuery):
    """
    chooseinline <custom_code> <data>
    """
    code = callback.data.split()

    state = get_state(callback.from_user.id, callback.message.chat.id)
    if data := await state.get_data():
        if not data:
            return

        func = data.get('function')
        transmitted_data = data.get('transmitted_data', {})
        custom_code = data.get('custom_code')

        if not func or custom_code is None:
            return

    code.pop(0)
    if code[0] == str(custom_code):
        code.pop(0)
        if len(code) == 1: code = code[0]

        transmitted_data['temp'] = {}
        transmitted_data['temp']['message_data'] = callback.message

        if 'steps' in transmitted_data and 'process' in transmitted_data:
            try:
                transmitted_data['steps'][transmitted_data['process']]['bmessageid'] = callback.message.message_id
            except Exception as e:
                print(f'ChooseInline error {e}')

        else: transmitted_data['bmessageid'] = callback.message.message_id

        if data['one_element']: await state.clear()

        try:
            await ChooseInlineHandler(**data).call_function(code)
        except Exception as e:
                print(f'ChooseInline call_function error {e}')
