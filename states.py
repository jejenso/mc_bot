from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    waiting_full_name = State()
    waiting_mc_nick = State()
    waiting_location = State()


class ReportForm(StatesGroup):
    waiting_text_server = State()
    waiting_text_tgk = State()


class AdminVerdict(StatesGroup):
    waiting_verdict = State()
