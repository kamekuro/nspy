"""Пример: работа с внутренней почтой — список, чтение, скачивание файлов."""

import asyncio
from io import BytesIO

from netschoolpy import NetSchoolAPI


async def main():
    async with NetSchoolAPI("https://sgo.example.ru") as ns:
        await ns.login("student_login", "password", "School Name")

        # Список входящих писем (первая страница)
        page = await ns.mail_list("Inbox", page=1, page_size=20)
        print(f"Всего писем: {page.total_items}")

        for entry in page.entries:
            print(f"  #{entry.id}  {entry.sent}  {entry.author}  «{entry.subject}»")

        # Прочитать первое письмо
        if page.entries:
            msg = await ns.mail_read(page.entries[0].id)
            print(f"\nПисьмо: {msg.subject}")
            print(f"От: {msg.author_name}")
            print(f"Текст: {msg.text}")

            # Скачать вложения
            for att in msg.file_attachments:
                buf = BytesIO()
                await ns.download_attachment(att.id, buf)
                with open(att.name, "wb") as f:
                    f.write(buf.getvalue())
                print(f"Скачан: {att.name} ({len(buf.getvalue())} байт)")

        # Отправленные
        sent = await ns.mail_list("Sent")
        print(f"\nОтправленных: {sent.total_items}")


asyncio.run(main())
