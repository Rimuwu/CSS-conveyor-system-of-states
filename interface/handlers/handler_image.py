from aiogram import F
from bot.main import botik as bot, css_router
from interface.state_handlers import ChooseImageHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import get_state

@css_router.message(F.photo, GeneralStates.ChooseImage)
async def ChooseImage(message: Message):
    """Общая функция для получения изображения
    """
    if not message.from_user or not message.from_user.id:
        return

    if not message.photo:
        await bot.send_message(message.chat.id, "❗ Пожалуйста, отправьте изображение."
                               )
        return

    userid = message.from_user.id
    state = get_state(userid, message.chat.id)

    if state and (data := await state.get_data()):
        transmitted_data = data.get('transmitted_data', {})

        await state.clear()

        if message.photo:
            fileID = message.photo[-1].file_id
            if 'temp' not in transmitted_data:
                transmitted_data['temp'] = {}
            transmitted_data['temp']['file'] = message.photo[-1]
        else:
            await bot.send_message(message.chat.id, "❗ Пожалуйста, отправьте изображение."
                               )
            return

        await ChooseImageHandler(**data).call_function(fileID)

@css_router.message(GeneralStates.ChooseImage)
async def ChooseImage_0(message: Message):
    """Общая функция для получения изображения
    """

    state = get_state(message.from_user.id, message.chat.id)
    if message.text == '0':
        if data := await state.get_data():
            need_image = data['need_image']

        if need_image:
            await state.clear()

            await ChooseImageHandler(**data).call_function('no_image')


