from aiogram.fsm.state import State, StatesGroup

class GeneralStates(StatesGroup):
    zero = State() # Состояние по умолчанию
    ChooseInt = State() # Состояние для ввода числа
    ChooseString = State() # Состояние для ввода текста
    ChooseConfirm = State() # Состояние для подтверждения (да / нет)
    ChooseOption = State() # Состояние для выбора среди вариантов
    ChooseInline = State() # Состояние для выбора кнопки
    ChoosePagesState = State() # Состояние для выбора среди вариантов, а так же поддерживает страницы
    ChooseCustom = State() # Состояние для кастомного обработчика
    ChooseTime = State() # Состояние для ввода времени
    ChooseImage = State() # Состояние для ввода загрузки изображения