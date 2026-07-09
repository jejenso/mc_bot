from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💰 Баланс сервера")],
        [KeyboardButton(text="📜 Правила"), KeyboardButton(text="📖 Инструкции")],
    ],
    resize_keyboard=True,
)


def profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="topup")],
        ]
    )


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile")]]
    )


def instructions_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔌 Как зайти на сервер", callback_data="instr_join")],
            [InlineKeyboardButton(text="🧩 Как установить моды", callback_data="instr_mods")],
            [InlineKeyboardButton(text="💳 Как пополнить баланс", callback_data="instr_topup")],
            [InlineKeyboardButton(text="📝 Как зарегистрироваться", callback_data="instr_register")],
        ]
    )


def admin_confirm_kb(tg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"adm_confirm:{tg_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_reject:{tg_id}"),
            ]
        ]
    )
