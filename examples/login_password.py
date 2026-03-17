import asyncio
import os
from netschoolpy import NetSchoolAPI


async def main():
    # Настройки
    url = os.getenv("NS_URL", "https://sgo.your-region.ru")
    login = os.getenv("NS_LOGIN", "student_login")
    password = os.getenv("NS_PASSWORD", "password")
    school = os.getenv("NS_SCHOOL", "My School Name")

    async with NetSchoolAPI(url) as ns:
        try:
            # Вход по логину и паролю
            print(f"Попытка входа в {url}...")
            await ns.login(login, password, school)

            print(f"Успешный вход! Студент: {ns._student_id}")

            # Получаем данные
            diary = await ns.diary()
            print(f"Расписание загружено, дней: {len(diary.schedule)}")

        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
