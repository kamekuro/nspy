import asyncio
import datetime
import os
import sys
from netschoolpy import NetSchoolAPI


async def main():
    url = os.getenv("NS_URL", "https://sgo.your-region.ru")

    if "your-region.ru" in url:
        print("❌ ОШИБКА: Не указан URL дневника (NS_URL).")
        return

    # SGO
    ns_login = os.getenv("NS_LOGIN")
    ns_password = os.getenv("NS_PASSWORD")
    ns_school = os.getenv("NS_SCHOOL")

    # ESIA
    esia_login = os.getenv("ESIA_LOGIN")
    esia_password = os.getenv("ESIA_PASSWORD")

    use_qr = "--qr" in sys.argv

    async with NetSchoolAPI(url) as ns:
        try:
            if use_qr:
                print("Вход через QR...")
                try:
                    import qrcode

                    async def qr_cb(data):
                        qr = qrcode.QRCode()
                        qr.add_data(data)
                        qr.print_ascii()
                        print("\n⚠️  ВАЖНО: QR-код действителен только 1 минуту!")
                        print("Отсканируйте QR-код в приложении Госуслуги -> Сканер")

                    await ns.login_via_gosuslugi_qr(qr_cb)
                except ImportError:
                    print("Нужен qrcode: pip install qrcode")
                    return
            elif esia_login and esia_password:
                await ns.login_via_gosuslugi(esia_login, esia_password)
            elif ns_login and ns_password:
                if not ns_school:
                    print("❌ Укажите NS_SCHOOL (название школы)")
                    return
                await ns.login(ns_login, ns_password, ns_school)
            else:
                print("Нет данных для входа. Используйте ENV или флаг --qr")
                return

            # Логика скрипта
            today = datetime.date.today()
            start = today - datetime.timedelta(days=30)
            end = today

            print(f"Считаем средний балл с {start} по {end}...")

            diary = await ns.diary(start=start, end=end)
            all_marks = []  # (mark, weight)

            for day in diary.schedule:
                for lesson in day.lessons:
                    for assignment in lesson.assignments:
                        if assignment.mark:
                            all_marks.append((assignment.mark, assignment.weight))

            if all_marks:
                simple_avg = sum(m for m, _ in all_marks) / len(all_marks)
                weighted_sum = sum(m * w for m, w in all_marks)
                weight_total = sum(w for _, w in all_marks)
                weighted_avg = weighted_sum / weight_total if weight_total else 0
                print(f"Простой средний балл: {simple_avg:.2f}")
                print(f"Средневзвешенный балл: {weighted_avg:.2f}")
            else:
                print("Оценок нет.")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
