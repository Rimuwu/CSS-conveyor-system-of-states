from bot.main import botik as bot, css_router
from interface.utils import get_state
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import F

async def cancel(message, text:str = "❌"):
    """ Команда общей отмены
    """
    if text:
        await bot.send_message(message.chat.id, text)

    state = get_state(message.from_user.id, message.chat.id)
    if state: await state.clear()

@css_router.message(F.containst('❌'))
async def cancel_m(message: Message):
    """ Команда отмены
    """
    await cancel(message)

@css_router.message(Command(commands=['cancel']))
async def cancel_c(message: Message):
    """ Команда отмены
    """
    await cancel(message)