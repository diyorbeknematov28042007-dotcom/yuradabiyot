from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database.db import CATEGORIES


def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📚 Kitoblarni yuklab olish"),
        KeyboardButton(text="🔍 Qidiruv")
    )
    builder.row(
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="ℹ️ Bot haqida")
    )
    return builder.as_markup(resize_keyboard=True)


def subscription_kb(channels: list):
    builder = InlineKeyboardBuilder()
    for ch in channels:
        name = ch.get("name") or ch["id"]
        link = ch.get("link") or f"https://t.me/{ch['id'].lstrip('@')}"
        builder.row(InlineKeyboardButton(text=f"➕ {name}", url=link))
    builder.row(InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription"))
    return builder.as_markup()


def directions_kb(directions: list):
    builder = InlineKeyboardBuilder()
    for d in directions:
        builder.row(InlineKeyboardButton(
            text=f"{d['emoji']} {d['name']}",
            callback_data=f"dir_{d['id']}"
        ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def books_list_kb(books: list, direction_id: int, page: int = 0, per_page: int = 8):
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    for b in books[start:end]:
        title = b["title"][:35] + "..." if len(b["title"]) > 35 else b["title"]
        builder.row(InlineKeyboardButton(
            text=f"📖 {title}",
            callback_data=f"book_{b['id']}"
        ))
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data=f"bookspage_{direction_id}_{page-1}"))
    if end < len(books):
        nav.append(InlineKeyboardButton(text="➡️", callback_data=f"bookspage_{direction_id}_{page+1}"))
    if nav:
        builder.row(*nav)
    builder.row(InlineKeyboardButton(text="⬅️ Yo'nalishlar", callback_data="books_panel"))
    return builder.as_markup()


def book_detail_kb(book_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📥 Yuklab olish", callback_data=f"download_{book_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Yo'nalishlar", callback_data="books_panel"))
    return builder.as_markup()


def search_results_kb(books: list):
    builder = InlineKeyboardBuilder()
    for b in books:
        title = b["title"][:30] + "..." if len(b["title"]) > 30 else b["title"]
        builder.row(InlineKeyboardButton(
            text=f"📖 {title} — {b['author']}",
            callback_data=f"book_{b['id']}"
        ))
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="main_menu"))
    return builder.as_markup()


def admin_panel_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📢 Ommaviy post", callback_data="admin_broadcast"))
    builder.row(InlineKeyboardButton(text="📚 Kitob qo'shish", callback_data="admin_add_book"))
    builder.row(InlineKeyboardButton(text="📊 Monitoring", callback_data="admin_monitoring"))
    builder.row(InlineKeyboardButton(text="📌 Majburiy kanallar", callback_data="admin_channels"))
    builder.row(InlineKeyboardButton(text="🗂 Yo'nalishlar", callback_data="admin_directions"))
    return builder.as_markup()


def admin_channels_kb(channels: list):
    builder = InlineKeyboardBuilder()
    for ch in channels:
        name = ch.get("name") or ch["id"]
        builder.row(InlineKeyboardButton(text=f"❌ {name}", callback_data=f"admin_del_ch_{ch['id']}"))
    builder.row(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="admin_add_channel"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin panel", callback_data="admin_back"))
    return builder.as_markup()


def admin_directions_kb(directions: list):
    builder = InlineKeyboardBuilder()
    for d in directions:
        builder.row(InlineKeyboardButton(
            text=f"❌ {d['emoji']} {d['name']}",
            callback_data=f"admin_del_dir_{d['id']}"
        ))
    builder.row(InlineKeyboardButton(text="➕ Yo'nalish qo'shish", callback_data="admin_add_direction"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin panel", callback_data="admin_back"))
    return builder.as_markup()


def categories_kb():
    builder = InlineKeyboardBuilder()
    for cat in CATEGORIES:
        builder.row(InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()


def direction_select_kb(directions: list):
    builder = InlineKeyboardBuilder()
    for d in directions:
        builder.row(InlineKeyboardButton(
            text=f"{d['emoji']} {d['name']}",
            callback_data=f"seldir_{d['id']}"
        ))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()


def confirm_broadcast_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_broadcast"),
        InlineKeyboardButton(text="❌ Bekor", callback_data="cancel_broadcast")
    )
    return builder.as_markup()


def back_to_admin_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Admin panel", callback_data="admin_back"))
    return builder.as_markup()
