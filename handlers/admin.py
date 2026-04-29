from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database.db import (
    add_book, get_all_directions, add_direction, delete_direction,
    get_mandatory_channels, add_mandatory_channel, remove_mandatory_channel,
    get_users_count, get_books_count, get_new_users_today, get_new_users_week,
    get_books_stats_by_direction, get_all_users, CATEGORIES
)
from keyboards.keyboards import (
    admin_panel_kb, admin_channels_kb, admin_directions_kb,
    categories_kb, direction_select_kb, confirm_broadcast_kb, back_to_admin_kb
)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ─── STATES ───────────────────────────────────────────────────────────────────

class AddBookState(StatesGroup):
    title = State()
    author = State()
    year = State()
    direction = State()
    category = State()
    subject = State()
    file = State()


class AddChannelState(StatesGroup):
    channel_id = State()
    channel_name = State()
    channel_link = State()


class AddDirectionState(StatesGroup):
    name = State()
    emoji = State()


class BroadcastState(StatesGroup):
    message = State()


# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz.")
        return
    await message.answer(
        "🔐 <b>Admin panel</b>\n\nNimani amalga oshirmoqchisiz?",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "🔐 <b>Admin panel</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Bekor qilindi.\n\n🔐 <b>Admin panel</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_kb())


# ─── MONITORING ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_monitoring")
async def admin_monitoring(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return

    users_total = await get_users_count()
    users_today = await get_new_users_today()
    users_week = await get_new_users_week()
    books_total = await get_books_count()
    stats = await get_books_stats_by_direction()

    text = (
        f"📊 <b>Monitoring</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"  • Jami: <b>{users_total}</b>\n"
        f"  • Bugun: <b>{users_today}</b>\n"
        f"  • Bu hafta: <b>{users_week}</b>\n\n"
        f"📚 <b>Kitoblar:</b> {books_total} ta\n\n"
        f"📂 <b>Yo'nalishlar:</b>\n"
    )
    for s in stats:
        text += f"\n  {s['emoji']} {s['direction']}: <b>{s['count']}</b>"

    await call.message.edit_text(text, reply_markup=back_to_admin_kb(), parse_mode="HTML")


# ─── MANDATORY CHANNELS ───────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_channels")
async def admin_channels(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    channels = await get_mandatory_channels()
    await call.message.edit_text(
        f"📌 <b>Majburiy kanallar</b> ({len(channels)} ta)\n\nO'chirish uchun bosing:",
        reply_markup=admin_channels_kb(channels),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_add_channel")
async def admin_add_channel_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AddChannelState.channel_id)
    await call.message.edit_text(
        "📌 <b>Kanal qo'shish</b>\n\n"
        "Kanal ID yoki @username kiriting:\n"
        "(Misol: @kanalim yoki -1001234567890)\n\n/cancel — bekor qilish",
        parse_mode="HTML"
    )


@router.message(AddChannelState.channel_id)
async def add_channel_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(channel_id=message.text.strip())
    await state.set_state(AddChannelState.channel_name)
    await message.answer("✏️ Kanal nomini kiriting:")


@router.message(AddChannelState.channel_name)
async def add_channel_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(channel_name=message.text.strip())
    await state.set_state(AddChannelState.channel_link)
    await message.answer("🔗 Kanal havolasini kiriting (https://t.me/...):")


@router.message(AddChannelState.channel_link)
async def add_channel_link(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    await add_mandatory_channel(data["channel_id"], data["channel_name"], message.text.strip())
    await state.clear()
    channels = await get_mandatory_channels()
    await message.answer(
        f"✅ Kanal qo'shildi!\n\n📌 <b>Kanallar</b> ({len(channels)} ta):",
        reply_markup=admin_channels_kb(channels),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_del_ch_"))
async def delete_channel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    channel_id = call.data.replace("admin_del_ch_", "")
    await remove_mandatory_channel(channel_id)
    channels = await get_mandatory_channels()
    await call.message.edit_text(
        f"✅ Kanal o'chirildi!\n\n📌 <b>Kanallar</b> ({len(channels)} ta):",
        reply_markup=admin_channels_kb(channels),
        parse_mode="HTML"
    )


# ─── DIRECTIONS ───────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_directions")
async def admin_directions(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    directions = await get_all_directions()
    await call.message.edit_text(
        f"🗂 <b>Yo'nalishlar</b> ({len(directions)} ta)\n\nO'chirish uchun bosing:",
        reply_markup=admin_directions_kb(directions),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_add_direction")
async def add_direction_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AddDirectionState.name)
    await call.message.edit_text(
        "🗂 <b>Yo'nalish qo'shish</b>\n\nYo'nalish nomini kiriting:\n\n/cancel — bekor qilish",
        parse_mode="HTML"
    )


@router.message(AddDirectionState.name)
async def add_direction_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AddDirectionState.emoji)
    await message.answer("😀 Emoji kiriting (masalan: ⚖️ yoki 📋):")


@router.message(AddDirectionState.emoji)
async def add_direction_emoji(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    await add_direction(data["name"], message.text.strip())
    await state.clear()
    directions = await get_all_directions()
    await message.answer(
        f"✅ Yo'nalish qo'shildi!\n\n🗂 <b>Yo'nalishlar</b> ({len(directions)} ta):",
        reply_markup=admin_directions_kb(directions),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_del_dir_"))
async def delete_direction_callback(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        return
    direction_id = int(call.data.replace("admin_del_dir_", ""))
    await delete_direction(direction_id)
    directions = await get_all_directions()
    await call.message.edit_text(
        f"✅ O'chirildi!\n\n🗂 <b>Yo'nalishlar</b> ({len(directions)} ta):",
        reply_markup=admin_directions_kb(directions),
        parse_mode="HTML"
    )


# ─── ADD BOOK ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_add_book")
async def add_book_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(AddBookState.title)
    await call.message.edit_text(
        "📚 <b>Kitob qo'shish</b>\n\n<b>1/7.</b> Kitob nomini kiriting:\n\n/cancel — bekor qilish",
        parse_mode="HTML"
    )


@router.message(AddBookState.title)
async def add_book_title(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(title=message.text.strip())
    await state.set_state(AddBookState.author)
    await message.answer("✍️ <b>2/7.</b> Muallif ismini kiriting:", parse_mode="HTML")


@router.message(AddBookState.author)
async def add_book_author(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.update_data(author=message.text.strip())
    await state.set_state(AddBookState.year)
    await message.answer("📅 <b>3/7.</b> Nashr yilini kiriting (o'tkazib yuborish: /skip):", parse_mode="HTML")


@router.message(AddBookState.year)
async def add_book_year(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    year = None
    if message.text.strip() != "/skip":
        try:
            year = int(message.text.strip())
        except ValueError:
            await message.answer("❌ To'g'ri yil kiriting yoki /skip yozing.")
            return
    await state.update_data(year=year)
    await state.set_state(AddBookState.direction)
    directions = await get_all_directions()
    await message.answer(
        "🗂 <b>4/7.</b> Yo'nalishni tanlang:",
        reply_markup=direction_select_kb(directions),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("seldir_"))
async def add_book_direction(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    direction_id = int(call.data.split("_")[1])
    await state.update_data(direction_id=direction_id)
    await state.set_state(AddBookState.category)
    await call.message.edit_text(
        "📑 <b>5/7.</b> Kategoriyani tanlang:",
        reply_markup=categories_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("cat_"))
async def add_book_category(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    category = call.data.replace("cat_", "")
    await state.update_data(category=category)
    await state.set_state(AddBookState.subject)
    await call.message.edit_text(
        "📚 <b>6/7.</b> Fan nomini kiriting (o'tkazib yuborish: /skip):",
        parse_mode="HTML"
    )


@router.message(AddBookState.subject)
async def add_book_subject(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    subject = None if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(subject=subject)
    await state.set_state(AddBookState.file)
    await message.answer("📄 <b>7/7.</b> Kitobning PDF faylini yuboring:", parse_mode="HTML")


@router.message(AddBookState.file, F.document)
async def add_book_file(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    doc = message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer("❌ Faqat PDF fayl yuboring!")
        return

    data = await state.get_data()
    await add_book(
        title=data["title"],
        author=data["author"],
        year=data.get("year"),
        direction_id=data["direction_id"],
        category=data.get("category"),
        subject=data.get("subject"),
        file_id=doc.file_id,
        added_by=message.from_user.id
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Kitob qo'shildi!</b>\n\n"
        f"📖 {data['title']}\n✍️ {data['author']}",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.message(AddBookState.file)
async def add_book_file_wrong(message: Message):
    await message.answer("❌ Iltimos, PDF fayl yuboring!")


# ─── BROADCAST ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return
    await state.set_state(BroadcastState.message)
    await call.message.edit_text(
        "📢 <b>Ommaviy post</b>\n\n"
        "Xabar, rasm yoki hujjat yuboring:\n\n/cancel — bekor qilish",
        parse_mode="HTML"
    )


@router.message(BroadcastState.message)
async def broadcast_preview(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    msg_data = {
        "text": message.text or message.caption,
        "photo": message.photo[-1].file_id if message.photo else None,
        "document": message.document.file_id if message.document else None,
    }
    await state.update_data(msg_data=msg_data)
    users_count = await get_users_count()
    await message.answer(
        f"📤 <b>{users_count}</b> ta foydalanuvchiga yuboriladi.\n\nTasdiqlaysizmi?",
        reply_markup=confirm_broadcast_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_broadcast")
async def broadcast_send(call: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(call.from_user.id):
        return
    data = await state.get_data()
    msg_data = data.get("msg_data", {})
    await state.clear()

    users = await get_all_users()
    sent = 0
    failed = 0

    await call.message.edit_text(f"📤 Yuborilmoqda... 0/{len(users)}")

    for i, user_id in enumerate(users):
        try:
            if msg_data.get("photo"):
                await bot.send_photo(user_id, photo=msg_data["photo"], caption=msg_data.get("text"), parse_mode="HTML")
            elif msg_data.get("document"):
                await bot.send_document(user_id, document=msg_data["document"], caption=msg_data.get("text"), parse_mode="HTML")
            elif msg_data.get("text"):
                await bot.send_message(user_id, msg_data["text"], parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

        if (i + 1) % 50 == 0:
            try:
                await call.message.edit_text(f"📤 Yuborilmoqda... {i+1}/{len(users)}")
            except Exception:
                pass

    await call.message.answer(
        f"✅ <b>Post yuborildi!</b>\n\n✔️ Muvaffaqiyatli: <b>{sent}</b>\n❌ Xatolik: <b>{failed}</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Bekor qilindi.\n\n🔐 <b>Admin panel</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )
