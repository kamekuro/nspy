import asyncio
import os
import sys
from netschoolpy import NetSchool


async def main():
    # Настройки приоритетов входа:
    # 1. QR-код (если запущен с --qr)
    # 2. ESIA Login/Password (если заданы ENV)
    # 3. SGO Login/Password (если заданы ENV)

    url = os.getenv("NS_URL", "https://sgo.your-region.ru")

    if "your-region.ru" in url:
        print("❌ ОШИБКА: Не указан URL дневника (NS_URL).")
        print("Пример: export NS_URL=https://sgo.tv-obr.ru")
        return

    # SGO
    ns_login = os.getenv("NS_LOGIN")
    ns_password = os.getenv("NS_PASSWORD")
    ns_school = os.getenv("NS_SCHOOL")

    # ESIA
    esia_login = os.getenv("ESIA_LOGIN")
    esia_password = os.getenv("ESIA_PASSWORD")

    # Флаг для QR
    use_qr = "--qr" in sys.argv

    ns = NetSchool(url)

    try:
        if use_qr:
            print(f"Вход через QR-код Госуслуг (URL: {url})...")

            try:
                import qrcode
            except ImportError:
                print(
                    "Ошибка: Для QR-входа нужно установить qrcode: pip install qrcode"
                )
                return

            async def qr_callback(qr_data):
                qr = qrcode.QRCode()
                qr.add_data(qr_data)
                qr.print_ascii()
                print("\n⚠️  ВАЖНО: QR-код действителен только 2 минуты!")
                print("Отсканируйте QR-код в приложении Госуслуги -> Сканер")

            await ns.login_via_gosuslugi_qr(qr_callback)

        elif esia_login and esia_password:
            print(f"Вход через Госуслуги (URL: {url})...")
            await ns.login_via_gosuslugi(esia_login, esia_password)

        elif ns_login and ns_password:
            if not ns_school:
                print("❌ Укажите NS_SCHOOL (название школы)")
                return
            print(f"Вход через логин/пароль школы (URL: {url})...")
            await ns.login(ns_login, ns_password, ns_school)

        else:
            print("❌ Не найдены данные для входа!")
            print("1. Укажите NS_LOGIN/NS_PASSWORD (для обычного входа)")
            print("2. Или ESIA_LOGIN/ESIA_PASSWORD (для Госуслуг)")
            print("3. Или запустите с флагом --qr (для входа по QR)")
            return

        print("✅ Успешный вход!")
        diary = await ns.diary()

        print("\nРасписание на неделю:")
        for day in diary.schedule:
            print(f"\nExample Day: {day.day}")
            for lesson in day.lessons:
                print(f"  {lesson.number}. {lesson.subject}")
                for assignment in lesson.assignments:
                    if assignment.mark:
                        print(
                            f"     Оценка: {assignment.mark} (вес: {assignment.weight}, тип: {assignment.kind_abbr})"
                        )

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await ns.close()


if __name__ == "__main__":
    asyncio.run(main())
