from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from config import TARIFFS

# --- Главное меню (reply-клавиатура, всегда видна снизу) ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="💳 Оплата"), KeyboardButton(text="📜 Правила")],
        [KeyboardButton(text="🚨 Репорт")],
    ],
    resize_keyboard=True,
)

def location_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)],
            [KeyboardButton(text="Пропустить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# --- Инлайн-клавиатуры ---

def tariff_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t["label"], callback_data=f"tariff:{key}")]
        for key, t in TARIFFS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def paid_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid_confirm")]
    ])


def rules_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Правила сервера", callback_data="rules:server")],
        [InlineKeyboardButton(text="💬 Правила тгк", callback_data="rules:tgk")],
    ])


def report_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Нарушение на сервере", callback_data="report:server")],
        [InlineKeyboardButton(text="💬 Нарушение в тгк", callback_data="report:tgk")],
    ])


# --- Админские инлайн-клавиатуры ---

def admin_registration_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"reg_ok:{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reg_no:{user_id}"),
        ]
    ])


def admin_payment_kb(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"pay_ok:{payment_id}")]
    ])


def admin_report_kb(report_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Рассмотреть жалобу", callback_data=f"report_review:{report_id}")]
    ])
