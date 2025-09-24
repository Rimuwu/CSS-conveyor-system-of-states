from bot.main import botik as bot, css_router
from interface.const import BACK_BUTTON, FORWARD_BUTTON
from interface.state_handlers import ChoosePagesStateHandler
from interface.states import GeneralStates
from aiogram.types import Message

from interface.utils import chunk_pages, get_state



@css_router.message(GeneralStates.ChoosePagesState)
async def ChooseOptionPages(message: Message):
    """Кастомный обработчик, принимает данные и отправляет в обработчик
    """
    chatid = message.chat.id

    state = get_state(message.from_user.id, message.chat.id)
    if data := await state.get_data():
        options: dict = data['options']
        transmitted_data: dict = data['transmitted_data']

        pages: list = data['pages']
        page: int = data['page']
        one_element: bool = data['one_element']

        settings: dict = data['settings']
        lang: str = data['lang']

    handler = ChoosePagesStateHandler(**data)

    if message.text in options.keys():
        if one_element: await state.clear()

        transmitted_data['options'] = options
        transmitted_data['key'] = message.text

        if 'steps' in transmitted_data and 'process' in transmitted_data:
            transmitted_data['steps'][transmitted_data['process']]['umessageid'] = message.message_id
        else: transmitted_data['umessageid'] = message.message_id

        res = await ChoosePagesStateHandler(**data).call_function(options[message.text])

        if not one_element and res and type(res) == dict and 'status' in res:
            # Удаляем состояние
            if res['status'] == 'reset': await state.clear()

            # Обновить все данные
            elif res['status'] == 'update' and 'options' in res:
                pages = chunk_pages(res['options'], settings['horizontal'], settings['vertical'])

                if 'page' in res: page = res['page']
                if page >= len(pages) - 1: page = 0

                await state.update_data(options=res['options'], pages=pages, page=page)
                await handler.call_update_page_function(pages, page, chatid, lang)

            # Добавить или удалить элемент
            elif res['status'] == 'edit' and 'elements' in res:
                
                for key, value in res['elements'].items():
                    if key == 'add':
                        for iter_key, iter_value in value.items():
                            options[iter_key] = iter_value
                    elif key == 'delete':
                        for i in value: del options[i]

                pages = chunk_pages(options, settings['horizontal'], settings['vertical'])

                if page >= len(pages) - 1: page = 0

                await state.update_data(options=options, pages=pages, page=page)
                await handler.call_update_page_function(pages, page, chatid, lang)

    elif message.text == BACK_BUTTON and len(pages) > 1:
        if page == 0: page = len(pages) - 1
        else: page -= 1

        if data.get('last_user_message'):
            await bot.delete_message(chatid, data['last_user_message'])

        await state.update_data(page=page)
        mes = await handler.call_update_page_function(pages, page, chatid, lang)
        if isinstance(mes, Message):
            mes_id = mes.message_id

            if data.get('last_updated_message'):
                await bot.delete_message(chatid, data['last_updated_message'])

            await state.update_data(last_updated_message=mes_id, last_user_message=message.message_id)

    elif message.text == FORWARD_BUTTON and len(pages) > 1:
        if page >= len(pages) - 1: page = 0
        else: page += 1

        if data.get('last_user_message'):
            await bot.delete_message(chatid, data['last_user_message'])

        await state.update_data(page=page)
        mes = await handler.call_update_page_function(pages, page, chatid, lang)
        if isinstance(mes, Message):
            mes_id = mes.message_id
            
            if data.get('last_updated_message'):
                await bot.delete_message(chatid, data['last_updated_message'])

            await state.update_data(last_updated_message=mes_id, last_user_message=message.message_id)
    else:
        await bot.send_message(message.chat.id, 
                    "❗ Пожалуйста, выберите один из предложенных вариантов."
                )
