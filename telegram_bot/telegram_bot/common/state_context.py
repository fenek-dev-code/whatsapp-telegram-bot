from aiogram.fsm.state import State, StatesGroup


class PaymentState(StatesGroup):
    PAYMENT = State()
    CONFIRM = State()

class CreateTarifState(StatesGroup):
    NAME = State()
    PRICE = State()
    LIMIT_SHOW = State()
    LIMIT_CATEGORY = State()
    PERIOD = State()
    CREATE = State()

    DELETE = State()
    CONFIRM = State()