import sqlite3


def init_db() -> None:
    with sqlite3.connect("reminders.db") as db:
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            remind_time TEXT NOT NULL
            )
            """)


def add_reminder(user_id, text, remind_time) -> None:
    with sqlite3.connect("reminders.db") as db:
        cursor = db.cursor()
        cursor.execute(
            """
        INSERT INTO reminders (user_id, text, remind_time)
        VALUES (?, ?, ?)
    """,
            (user_id, text, remind_time),
        )


def get_user_reminders(user_id):
    with sqlite3.connect("reminders.db") as db:
        cursor = db.cursor()
        cursor.execute(
            """
                SELECT id, text, remind_time FROM reminders
                WHERE user_id = ?
            """,
            (user_id,),
        )
        result = cursor.fetchall()

        return result


def delete_reminder(reminder_id):
    with sqlite3.connect("reminders.db") as db:
        cursor = db.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
