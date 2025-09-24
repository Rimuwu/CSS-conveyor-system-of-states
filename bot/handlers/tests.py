from interface.state_handlers import *
from bot.main import botik as bot, test_router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove

from interface.utils import list_to_inline


async def end_int(number, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You entered int: {number}")

@test_router.message(Command('int'))
async def test_int(message: Message):
    await message.answer("Enter int")

    await ChooseIntHandler(end_int,
        message.from_user.id, message.chat.id, 
                           message.from_user.language_code,
                           min_int=10, max_int=100, transmitted_data={}
                           ).start()


async def end_string(string, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You entered string: {string}")

@test_router.message(Command('string'))
async def test_string(message: Message):
    await message.answer("Enter string")

    await ChooseStringHandler(end_string,
        message.from_user.id, message.chat.id, 
                              message.from_user.language_code,
                              min_len=1, max_len=50, transmitted_data={}
                              ).start()


async def end_time(time_str, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You entered time: {time_str}")

@test_router.message(Command('time'))
async def test_time(message: Message):
    await message.answer("Enter time")

    await ChooseTimeHandler(end_time,
        message.from_user.id, message.chat.id, 
                            message.from_user.language_code,
                            min_int=1, max_int=24, transmitted_data={}
                            ).start()


async def end_confirm(answer, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"Your answer: {'Yes' if answer else 'No'}")

@test_router.message(Command('confirm'))
async def test_confirm(message: Message):
    await message.answer("Do you confirm?",
                         reply_markup=list_to_keyboard(
                             ["Да", "Нет"]
                         )
                         )

    await ChooseConfirmHandler(end_confirm,
        message.from_user.id, message.chat.id, 
                               message.from_user.language_code,
                               cancel=False, transmitted_data={}
                               ).start()


async def end_option(selected_option, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You selected: {selected_option}",
                           reply_markup=ReplyKeyboardRemove())

@test_router.message(Command('option'))
async def test_option(message: Message):

    options = {
        "Option 1": "option1_data",
        "Option 2": "option2_data", 
        "Option 3": "option3_data"
    }

    await message.answer("Choose an option",
                         reply_markup=list_to_keyboard(
                             options.keys()
                         )
                         )

    await ChooseOptionHandler(end_option,
        message.from_user.id, message.chat.id,
                              message.from_user.language_code,
                              options=options, transmitted_data={}
                              ).start()


async def end_inline(answer, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You selected inline: {answer}")

@test_router.message(Command('inline'))
async def test_inline(message: Message):
    await message.answer("Click inline button",
                         reply_markup=list_to_inline(
                                [
                                    {'text': 'Inline 1', 'callback_data': 'chooseinline test inline_1'},
                                    {'text': 'Inline 2', 'callback_data': 'chooseinline test inline_2'},
                                    {'text': 'Inline 3', 'callback_data': 'chooseinline test inline_3'}
                                ], row_width=2
                         ) )

    await ChooseInlineHandler(end_inline,
        message.from_user.id, message.chat.id,
                              message.from_user.language_code,
                              custom_code="test", transmitted_data={}
                              ).start()


async def custom_handler(message, transmitted_data):
    # Пример кастомной проверки - принимаем только сообщения длиной больше 5 символов
    if message.text and len(message.text) > 5:
        return True, message.text.upper()
    return False, None

async def end_custom(result, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"Custom handler result: {result}")

@test_router.message(Command('custom'))
async def test_custom(message: Message):
    await message.answer("Enter text (more than 5 characters)")

    await ChooseCustomHandler(end_custom,
        custom_handler, message.from_user.id, message.chat.id,
                              message.from_user.language_code,
                              transmitted_data={}
                              ).start()


async def end_pages(selected_item, transmitted_data):
    result = transmitted_data.get('result', {})
    if result.get('status') == 'reset':
        await bot.send_message(transmitted_data['chatid'], "Pages selection completed")
        return {'status': 'reset'}
    else:
        await bot.send_message(transmitted_data['chatid'], f"You selected from pages: {selected_item}")

@test_router.message(Command('pages'))
async def test_pages(message: Message):
    await message.answer("Choose from pages")

    options = {}
    for i in range(1, 21):  # 20 элементов для демонстрации пагинации
        options[f"Item {i}"] = f"item_{i}_data"

    await ChoosePagesStateHandler(end_pages,
        message.from_user.id, message.chat.id,
                                  message.from_user.language_code,
                                  options=options, horizontal=2, vertical=3,
                                  one_element=False, transmitted_data={}
                                  ).start()


async def end_image(image_url, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], f"You sent image: {image_url}")

@test_router.message(Command('image'))
async def test_image(message: Message):
    await message.answer("Send an image")

    await ChooseImageHandler(end_image,
        message.from_user.id, message.chat.id,
                             message.from_user.language_code,
                             need_image=True, transmitted_data={}
                             ).start()


async def end_step_sequence(result_data, transmitted_data):
    await bot.send_message(transmitted_data['chatid'], 
                          f"Step sequence completed! Results: {result_data}")

@test_router.message(Command('steps'))
async def test_steps(message: Message):
    await message.answer("Starting step sequence")

    from interface.steps_datatype import IntStepData, StringStepData, ConfirmStepData, StepMessage

    steps = [
        IntStepData(
            name='user_age',
            message=StepMessage('Введите ваш возраст (1-100)'),
            data={'min_int': 1, 'max_int': 100}
        ),
        StringStepData(
            name='user_name', 
            message=StepMessage('Введите ваше имя'),
            data={'min_len': 2, 'max_len': 30}
        ),
        ConfirmStepData(
            name='confirmation',
            message=StepMessage('Подтвердите ваши данные?'),
            data={'cancel': False}
        )
    ]

    await ChooseStepHandler(end_step_sequence,
        message.from_user.id, message.chat.id,
                            message.from_user.language_code,
                            steps=steps, transmitted_data={}
                            ).start()

@test_router.message(Command('help'))
async def help_command(message: Message):
    help_text = """
        Available test commands:

        /int - Test integer input (10-100)
        /string - Test string input (1-50 chars)
        /time - Test time input (1-24 hours)
        /confirm - Test confirmation dialog
        /option - Test option selection
        /inline - Test inline button
        /custom - Test custom handler (>5 chars)
        /pages - Test paginated selection
        /image - Test image upload
        /steps - Test step sequence
        /cancel - Cancel current operation
        /help - Show this help message
        """
    await message.answer(help_text)