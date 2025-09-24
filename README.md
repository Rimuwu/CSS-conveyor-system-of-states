# CSS - Conveyor System of States

**Конвейерная система состояний для Telegram ботов на aiogram 3.x**

## Описание

CSS (Conveyor System of States) - это мощная библиотека для создания интерактивных диалогов в Telegram ботах с использованием aiogram 3.x. Система предоставляет удобный механизм для работы с состояниями пользователей и создания сложных пошаговых интерфейсов.

## Особенности

- 🔄 **Конвейерная обработка состояний** - пошаговое выполнение действий с сохранением контекста
- 🎯 **Типизированные обработчики** - встроенная поддержка различных типов ввода (числа, строки, подтверждения, выбор вариантов)
- 📄 **Поддержка пагинации** - автоматическое разбиение больших списков на страницы
- 🔧 **Расширяемость** - легко добавляйте новые типы обработчиков
- 💾 **Передача данных** - сохранение и передача данных между состояниями
- ❌ **Отмена операций** - встроенная поддержка отмены действий

## Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка окружения

1. Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=ваш_токен_бота
```

2. Запустите бота:
```bash
python main.py
```

## Типы состояний

Система поддерживает следующие типы состояний:

### 1. `ChooseInt` - Ввод числа
```python
await ChooseIntHandler(callback_function,
    user_id, chat_id, lang,
    min_int=10, max_int=100,
    transmitted_data={}
).start()
```

### 2. `ChooseString` - Ввод текста
```python
await ChooseStringHandler(callback_function,
    user_id, chat_id, lang,
    min_len=1, max_len=255,
    transmitted_data={}
).start()
```

### 3. `ChooseConfirm` - Подтверждение (Да/Нет)
```python
await ChooseConfirmHandler(callback_function,
    user_id, chat_id, lang,
    transmitted_data={}
).start()
```

### 4. `ChooseOption` - Выбор из вариантов
```python
await ChooseOptionHandler(callback_function,
    user_id, chat_id, lang,
    options={"key1": "Вариант 1", "key2": "Вариант 2"},
    transmitted_data={}
).start()
```

### 5. `ChooseInline` - Inline кнопки
```python
await ChooseInlineHandler(callback_function,
    user_id, chat_id, lang,
    inline_options={"key1": "Кнопка 1", "key2": "Кнопка 2"},
    transmitted_data={}
).start()
```

### 6. `ChoosePages` - Выбор с пагинацией
```python
await ChoosePagesHandler(callback_function,
    user_id, chat_id, lang,
    options=large_options_dict,
    horizontal=2, vertical=3,
    transmitted_data={}
).start()
```

### 7. `ChooseTime` - Ввод времени
```python
await ChooseTimeHandler(callback_function,
    user_id, chat_id, lang,
    transmitted_data={}
).start()
```

### 8. `ChooseImage` - Загрузка изображения
```python
await ChooseImageHandler(callback_function,
    user_id, chat_id, lang,
    transmitted_data={}
).start()
```

### 9. `ChooseCustom` - Кастомный обработчик
```python
await ChooseCustomHandler(callback_function,
    user_id, chat_id, lang,
    custom_handler=your_custom_handler,
    transmitted_data={}
).start()
```

## Пример использования

```python
from interface.state_handlers import ChooseIntHandler, ChooseStringHandler
from bot.main import bot

async def process_name(name, transmitted_data):
    """Обработка имени пользователя"""
    transmitted_data['name'] = name
    
    # Переход к следующему состоянию - ввод возраста
    await ChooseIntHandler(
        process_age,
        transmitted_data['userid'], 
        transmitted_data['chatid'], 
        transmitted_data['lang'],
        min_int=1, max_int=120,
        transmitted_data=transmitted_data
    ).start()

async def process_age(age, transmitted_data):
    """Обработка возраста пользователя"""
    name = transmitted_data['name']
    await bot.send_message(
        transmitted_data['chatid'], 
        f"Привет, {name}! Тебе {age} лет."
    )

@router.message(Command('start'))
async def start_registration(message: Message):
    """Начало регистрации пользователя"""
    await message.answer("Введите ваше имя:")
    
    await ChooseStringHandler(
        process_name,
        message.from_user.id,
        message.chat.id,
        message.from_user.language_code,
        min_len=2, max_len=50,
        transmitted_data={
            'userid': message.from_user.id,
            'chatid': message.chat.id,
            'lang': message.from_user.language_code
        }
    ).start()
```

## Метод этапов (Step System)

CSS предоставляет мощную систему пошагового выполнения операций через `ChooseStepHandler`. Этот метод позволяет создавать последовательности из различных типов состояний, которые выполняются друг за другом с автоматической передачей данных между этапами.

### Основные преимущества метода этапов:

- 🔄 **Автоматическая последовательность** - этапы выполняются один за другим без дополнительной логики
- 📝 **Сохранение результатов** - результат каждого этапа сохраняется и передается в финальную функцию
- 🎯 **Типизированные этапы** - используются те же обработчики, что и для отдельных состояний
- 🔗 **Передача контекста** - данные передаются между всеми этапами через `transmitted_data`
- ❌ **Обработка отмены** - автоматическая поддержка отмены на любом этапе

### Использование ChooseStepHandler

```python
from interface.state_handlers import ChooseStepHandler
from interface.steps_datatype import IntStepData, StringStepData, ConfirmStepData, StepMessage

async def process_registration_results(results, transmitted_data):
    """Финальная обработка результатов всех этапов"""
    age = results['user_age']
    name = results['user_name'] 
    confirmed = results['confirmation']
    
    if confirmed:
        await bot.send_message(
            transmitted_data['chatid'],
            f"Регистрация завершена!\nИмя: {name}\nВозраст: {age}"
        )
    else:
        await bot.send_message(
            transmitted_data['chatid'],
            "Регистрация отменена."
        )

@router.message(Command('register'))
async def start_multi_step_registration(message: Message):
    """Запуск многошаговой регистрации"""
    
    # Определяем последовательность этапов
    steps = [
        IntStepData(
            name='user_age',  # Ключ для сохранения результата
            message=StepMessage('Введите ваш возраст (18-99)'),
            data={'min_int': 18, 'max_int': 99}
        ),
        StringStepData(
            name='user_name',
            message=StepMessage('Введите ваше полное имя'),
            data={'min_len': 2, 'max_len': 50}
        ),
        ConfirmStepData(
            name='confirmation',
            message=StepMessage('Подтвердите регистрацию?'),
            data={'cancel': False}
        )
    ]
    
    await message.answer("Начинаем регистрацию...")
    
    await ChooseStepHandler(
        process_registration_results,  # Функция для обработки результатов
        message.from_user.id,
        message.chat.id,
        message.from_user.language_code,
        steps=steps,
        transmitted_data={
            'userid': message.from_user.id,
            'chatid': message.chat.id,
            'start_time': datetime.now()
        }
    ).start()
```

### Типы данных для этапов

Каждый этап определяется через специальный класс данных:

#### IntStepData - Ввод числа
```python
IntStepData(
    name='step_name',  # Имя для сохранения результата
    message=StepMessage('Введите число от 1 до 100'),
    data={'min_int': 1, 'max_int': 100}
)
```

#### StringStepData - Ввод текста
```python
StringStepData(
    name='user_input',
    message=StepMessage('Введите текст'),
    data={'min_len': 1, 'max_len': 255}
)
```

#### ConfirmStepData - Подтверждение
```python
ConfirmStepData(
    name='user_choice',
    message=StepMessage('Подтвердите действие?'),
    data={'cancel': True}  # Можно ли отменить операцию
)
```

#### OptionStepData - Выбор из вариантов
```python
OptionStepData(
    name='selected_option',
    message=StepMessage('Выберите вариант:'),
    data={
        'options': {
            'option1': 'Первый вариант',
            'option2': 'Второй вариант',
            'option3': 'Третий вариант'
        }
    }
)
```

#### InlineStepData - Inline кнопки
```python
InlineStepData(
    name='button_choice',
    message=StepMessage('Нажмите кнопку:'),
    data={
        'inline_options': {
            'btn1': 'Кнопка 1',
            'btn2': 'Кнопка 2'
        },
        'delete_markup': True  # Удалить кнопки после выбора
    }
)
```

#### TimeStepData - Ввод времени
```python
TimeStepData(
    name='selected_time',
    message=StepMessage('Введите время в формате ЧЧ:ММ'),
    data={}
)
```

#### ImageStepData - Загрузка изображения
```python
ImageStepData(
    name='uploaded_image',
    message=StepMessage('Загрузите изображение'),
    data={'need_image': True}
)
```

### StepMessage - Настройка сообщений

`StepMessage` позволяет настроить отправляемое пользователю сообщение:

```python
StepMessage(
    text='Текст сообщения',
    markup=keyboard,  # ReplyKeyboardMarkup или InlineKeyboardMarkup
    translate_message=False,  # Использовать систему переводов
    text_data={'key': 'value'},  # Данные для форматирования текста
    image='path/to/image.jpg',  # Путь к изображению
    parse_mode='Markdown'  # Режим парсинга текста
)
```

### Обработка результатов

Финальная функция получает два параметра:

1. **`results`** - словарь с результатами всех этапов:
```python
{
    'user_age': 25,
    'user_name': 'Иван Петров', 
    'confirmation': True
}
```

2. **`transmitted_data`** - словарь с данными, передаваемыми между этапами:
```python
{
    'userid': 123456789,
    'chatid': 987654321,
    'lang': 'ru',
    'start_time': datetime.now(),
    # ... другие пользовательские данные
}
```

### Дополнительные возможности

#### Повторяющиеся имена этапов
Если несколько этапов имеют одинаковое имя, их результаты сохраняются в виде списка:

```python
steps = [
    StringStepData(name='item', message=StepMessage('Введите товар 1')),
    StringStepData(name='item', message=StepMessage('Введите товар 2')),  
    StringStepData(name='item', message=StepMessage('Введите товар 3'))
]

# Результат: {'item': ['товар1', 'товар2', 'товар3']}
```

#### Этапы обновления данных (BaseUpdateType)
Можно добавлять промежуточные этапы для обновления `transmitted_data`:

```python
# Кастомный этап обновления (требует дополнительной реализации)
class CustomUpdateStep(BaseUpdateType):
    async def update_data(self, transmitted_data):
        # Логика обновления данных
        transmitted_data['processed'] = True
        return transmitted_data, 'update_result'
```

### Пример сложного многоэтапного процесса

```python
async def process_order(results, transmitted_data):
    """Обработка заказа после всех этапов"""
    category = results['category']
    items = results['items']  # Список товаров
    quantity = results['quantity']
    delivery = results['delivery_needed']
    
    total_price = calculate_price(category, items, quantity)
    
    if delivery:
        total_price += 200  # Стоимость доставки
        
    await bot.send_message(
        transmitted_data['chatid'],
        f"Заказ оформлен!\n"
        f"Категория: {category}\n"
        f"Товары: {', '.join(items)}\n"
        f"Количество: {quantity}\n"
        f"Доставка: {'Да' if delivery else 'Нет'}\n"
        f"Итого: {total_price} руб."
    )

@router.message(Command('order'))
async def create_order(message: Message):
    """Создание заказа через несколько этапов"""
    
    steps = [
        OptionStepData(
            name='category',
            message=StepMessage('Выберите категорию:'),
            data={
                'options': {
                    'electronics': 'Электроника',
                    'clothing': 'Одежда',
                    'books': 'Книги'
                }
            }
        ),
        StringStepData(
            name='items',
            message=StepMessage('Введите первый товар:'),
            data={'min_len': 1, 'max_len': 100}
        ),
        StringStepData(
            name='items',  # Повторяющееся имя - создастся список
            message=StepMessage('Введите второй товар (или напишите "нет"):'),
            data={'min_len': 1, 'max_len': 100}
        ),
        IntStepData(
            name='quantity',
            message=StepMessage('Введите количество:'),
            data={'min_int': 1, 'max_int': 99}
        ),
        ConfirmStepData(
            name='delivery_needed',
            message=StepMessage('Нужна доставка?'),
            data={'cancel': False}
        )
    ]
    
    await ChooseStepHandler(
        process_order,
        message.from_user.id,
        message.chat.id, 
        message.from_user.language_code,
        steps=steps,
        transmitted_data={'order_id': generate_order_id()}
    ).start()
```

## Структура проекта

```
CSS-conveyor-system-of-states/
├── main.py                          # Точка входа
├── requirements.txt                 # Зависимости
├── bot/                            # Основная логика бота
│   ├── main.py                     # Инициализация бота и диспетчера
│   └── handlers/                   # Обработчики команд и тестовые примеры
├── interface/                      # Система состояний
│   ├── states.py                   # Определения состояний
│   ├── state_handlers.py           # Базовые обработчики состояний
│   ├── steps_datatype.py          # Типы данных для шагов
│   ├── utils.py                    # Вспомогательные функции
│   ├── const.py                    # Константы
│   └── handlers/                   # Специфичные обработчики состояний
│       ├── handler_bool.py         # Обработчик подтверждений
│       ├── handler_custom.py       # Кастомные обработчики
│       ├── handler_image.py        # Обработчик изображений
│       ├── handler_inline.py       # Обработчик inline кнопок
│       └── ...                     # Другие обработчики
```

## API Reference

### BaseStateHandler

Базовый класс для всех обработчиков состояний.

**Параметры конструктора:**
- `function`: Callback-функция для обработки результата
- `userid`: ID пользователя
- `chatid`: ID чата
- `lang`: Язык пользователя
- `transmitted_data`: Словарь с передаваемыми данными между состояниями
- `message`: Объект сообщения (опционально)
- `messages_list`: Список ID сообщений (опционально)

### Utility функции

- `get_state(user_id, chat_id)` - получение FSM контекста
- `chunks(lst, n)` - разбиение списка на части
- `chunk_pages(options, horizontal, vertical)` - создание пагинации
- `list_to_keyboard(buttons)` - создание клавиатуры из списка
- `func_to_str(func)` - сериализация функции в строку
- `str_to_func(func_path)` - десериализация функции из строки

## Настройка

### Константы

В файле `interface/const.py` можно настроить:

```python
BACK_BUTTON = "◀"         # Кнопка "Назад"
FORWARD_BUTTON = "▶"      # Кнопка "Вперед"  
CANCEL_BUTTON = "❌ Отмена" # Кнопка "Отмена"
```

### Добавление новых состояний

1. Добавьте новое состояние в `interface/states.py`:
```python
class GeneralStates(StatesGroup):
    # ... существующие состояния
    YourNewState = State()  # Ваше новое состояние
```

2. Создайте обработчик в `interface/handlers/`:
```python
from interface.state_handlers import BaseStateHandler

class YourNewStateHandler(BaseStateHandler):
    state_name = 'YourNewState'
    
    # Ваша логика обработки
```

3. Зарегистрируйте обработчик в соответствующем router.

## Поддержка

Если у вас возникли вопросы или проблемы, создайте Issue в репозитории проекта.