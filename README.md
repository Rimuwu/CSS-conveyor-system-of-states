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