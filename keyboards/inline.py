from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎲 Рандомный факт", callback_data="random"),
        InlineKeyboardButton(text="💬 ChatGPT", callback_data="gpt")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Диалог с личностью", callback_data="talk"),
        InlineKeyboardButton(text="❓ Квиз", callback_data="quiz")
    )
    builder.row(
        InlineKeyboardButton(text="🌐 Переводчик", callback_data="translate"),
        InlineKeyboardButton(text="🎤 Голосовой чат", callback_data="voice")
    )
    return builder.as_markup()

def get_end_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏁 Закончить", callback_data="start"))
    return builder.as_markup()

def get_random_fact_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Хочу ещё факт", callback_data="random"),
        InlineKeyboardButton(text="🏁 Закончить", callback_data="start")
    )
    return builder.as_markup()

def get_personality_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧠 Эйнштейн", callback_data="personality_einstein"),
        InlineKeyboardButton(text="📜 Шекспир", callback_data="personality_shakespeare")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Тесла", callback_data="personality_tesla"),
        InlineKeyboardButton(text="👑 Клеопатра", callback_data="personality_cleopatra")
    )
    builder.row(InlineKeyboardButton(text="🏁 Закончить", callback_data="start"))
    return builder.as_markup()

def get_quiz_topic_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔬 Наука", callback_data="quiz_science"),
        InlineKeyboardButton(text="📚 История", callback_data="quiz_history")
    )
    builder.row(
        InlineKeyboardButton(text="🌍 География", callback_data="quiz_geography"),
        InlineKeyboardButton(text="📖 Литература", callback_data="quiz_literature")
    )
    builder.row(InlineKeyboardButton(text="🏁 Закончить", callback_data="start"))
    return builder.as_markup()

def get_quiz_after_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Ещё вопрос", callback_data="quiz_same_topic"),
        InlineKeyboardButton(text="📝 Сменить тему", callback_data="quiz")
    )
    builder.row(InlineKeyboardButton(text="🏁 Закончить", callback_data="start"))
    return builder.as_markup()

def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇬🇧 Английский", callback_data="lang_en"),
        InlineKeyboardButton(text="🇪🇸 Испанский", callback_data="lang_es")
    )
    builder.row(
        InlineKeyboardButton(text="🇫🇷 Французский", callback_data="lang_fr"),
        InlineKeyboardButton(text="🇩🇪 Немецкий", callback_data="lang_de")
    )
    builder.row(
        InlineKeyboardButton(text="🇮🇹 Итальянский", callback_data="lang_it"),
        InlineKeyboardButton(text="🇯🇵 Японский", callback_data="lang_ja")
    )
    builder.row(InlineKeyboardButton(text="🏁 Закончить", callback_data="start"))
    return builder.as_markup()

def get_translate_after_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Сменить язык", callback_data="translate"),
        InlineKeyboardButton(text="🏁 Закончить", callback_data="start")
    )
    return builder.as_markup()