# Css-conveyor system of states - Конвейерная Система Состояний

### ⌛ Зависимость

- Все функции написано под [TeleBot❤](https://github.com/eternnoir/pyTelegramBotAPI)

### 🎩 О функциях бота

- В коде реализованы функции для обработки данных получаемых от пользователя, а так же для их приятного отображения
- Так же представлена система, позволяющая на примере конвейеров создавать список нужных данных.

### 🛠 Для запуска бота
- Установите 3-ю версию пайтона (3.8+)
- Далее, установите все библиотеки из файла requirements.txt
>
    # Windows
    pip install requirements.txt

>
    # Linux
    pip install -r requirements.txt

- Вставте токен бота в bot/exec.py
- Запустите main.py
- Бинго!

### 🗻 Демо

- Все файлы команд лежат в handlers
- Вся основная система лежит в modules, а обработчик для них в handlers/states.py


### 🚗 Команды 
Для отмены состояния напиши /cancel или нажми кнопку отмены
- /pages - ChoosePagesState выбор опции по страницам
- /options - ChooseOptionState выбор опции но без страниц (более лёгкий)
- /int - ChooseIntState ввод числа
- /str - ChooseStringState ввод строки
- /bool - ChooseConfirmState да / нет
- /del_12 - ChooseCustomState пример кастомного обработчика
- ---------------
- /css - ChooseStepState получение большого количества данных, с помощью малого количества кода
