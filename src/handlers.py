from datetime import datetime
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database import add_reminder, get_user_reminders, delete_reminder


rt = Router()


class Reminder(StatesGroup):
    text = State()
    time = State()


@rt.message(CommandStart())
async def command_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name} 👋\n\nСписок команд:\n/add - Добавляет напоминание ➕\n/list - Просмотр всех активных напоминаний 📋\n/delete - Удаление напоминания ➖"
    )


@rt.message(Command("add"))
async def command_add(message: Message, state: FSMContext):
    await state.set_state(Reminder.text)
    await message.answer(
        'Как будет называться новое напоминание?\n❗ Если хочешь отменить создание напиши "ОТМЕНА"'
    )


@rt.message(Reminder.text)
async def reminder_text(message: Message, state: FSMContext):
    if message.text == "ОТМЕНА":
        await state.clear()
        await message.answer("Отменено ✅")
    else:
        await state.update_data(text=message.text)
        await state.set_state(Reminder.time)
        await message.answer("Введи время напоминания (18:30)")


@rt.message(Reminder.time)
async def reminder_time(message: Message, state: FSMContext):
    user_input = message.text.strip()

    try:
        valid_time = datetime.strptime(user_input, "%H:%M")
    except ValueError:
        await message.answer(
            "⛔ Неверный формат времени. Введи время в формате HH:MM, например 18:45."
        )
        return

    await state.update_data(time=user_input)
    data = await state.get_data()

    add_reminder(message.from_user.id, data["text"], data["time"])
    await message.answer(
        f"{data["text"]} - {data["time"]}\nНапоминание успешно создано!"
    )
    await state.clear()


@rt.message(Command("list"))
async def command_list(message: Message):
    reminders = get_user_reminders(message.from_user.id)

    if not reminders:
        await message.answer("У тебя пока нет ни одного напоминания.")
        return

    text_lines = ["📝 Твои напоминания:"]

    for idx, (rem_id, text, time) in enumerate(reminders, start=1):
        text_lines.append(f"{idx}. {text} - {time}")

    responce = "\n".join(text_lines)
    await message.answer(responce)


@rt.message(Command("delete"))
async def command_delete(message: Message):
    reminders = get_user_reminders(message.from_user.id)
    if not reminders:
        await message.answer("У тебя нет напоминаний для удаления.")
        return
    kb = InlineKeyboardBuilder()

    for rem_id, text, time in reminders:
        display = f"{text} - {time}"
        kb.button(text=display, callback_data=f"delete:{rem_id}")

    await message.answer(
        "Выбери напоминание, которое хочешь удалить:", reply_markup=kb.as_markup()
    )


@rt.callback_query(F.data.startswith("delete:"))
async def process_delete_callback(callback_query: CallbackQuery):
    reminder_id = int(callback_query.data.split(":")[1])
    delete_reminder(reminder_id)

    await callback_query.answer("Удалено ✅")
    await callback_query.message.edit_text("Напоминание удалено.")
