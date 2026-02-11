from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    name = State()
    phone = State()


class NewOrderStates(StatesGroup):
    select_address = State()
    enter_city = State()
    enter_district = State()
    enter_street = State()
    enter_house = State()
    enter_jv_qty = State()
    enter_lv_qty = State()
    enter_comment = State()
    confirm = State()


class EditOrderStates(StatesGroup):
    select_field = State()
    enter_jv_qty = State()
    enter_lv_qty = State()
    enter_comment = State()


class RescheduleStates(StatesGroup):
    enter_date = State()
    enter_comment = State()


class AddAddressStates(StatesGroup):
    enter_city = State()
    enter_district = State()
    enter_street = State()
    enter_house = State()
