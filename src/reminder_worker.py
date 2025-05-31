import asyncio
import sqlite3
from datetime import datetime


async def check_reminders(bot):
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        with sqlite3.connect("reminders.db") as db:
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT id, user_id, text
                FROM reminders
                WHERE remind_time = ?
            """,
                (current_time,),
            )

            rows = cursor.fetchall()
            for row in rows:
                rem_id, user_id, text = row

                await bot.send_message(user_id, f"⏰ Напоминание:\n{text}")
                cursor.execute("DELETE FROM reminders WHERE id = ?", (rem_id,))

        await asyncio.sleep(60)
