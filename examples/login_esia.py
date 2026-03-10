import asyncio
import os
from netschoolpy import NetSchoolAPI


async def main():
    # Настройки
    url = os.getenv("NS_URL", "https://sgo.your-region.ru")

    # Логин и пароль от Госуслуг
    esia_login = os.getenv("ESIA_LOGIN", "79000000000")
    esia_password = os.getenv("ESIA_PASSWORD", "gosuslugi_pass")

    async with NetSchoolAPI(url) as ns:
        try:
            print("Вход через Госуслуги (ESIA)...")

            # Метод login_via_gosuslugi проходит полный цикл авторизации.
            # Параметр school= нужен, если к аккаунту привязано несколько организаций.
            await ns.login_via_gosuslugi(
                esia_login, esia_password, school=os.getenv("NS_SCHOOL")
            )

            print("Успешный вход через ESIA!")

            diary = await ns.diary()
            print(
                f"Дневник получен. Уроков на неделе: {sum(len(d.lessons) for d in diary.schedule)}"
            )

        except Exception as e:
            print(f"Ошибка входа: {e}")


if __name__ == "__main__":
    asyncio.run(main())
