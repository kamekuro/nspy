import asyncio
import os
import sys

try:
    import qrcode
except ImportError:
    print("Для работы этого примера установите библиотеку qrcode:")
    print("pip install netschoolpy[qr]")
    print("или pip install qrcode")
    sys.exit(1)

from netschoolpy import NetSchool


async def main():
    url = os.getenv("NS_URL", "https://sgo.your-region.ru")

    # Callback-функция, которая будет вызвана библиотекой
    # Она получает строку `qr_data`, которую нужно превратить в QR-код
    async def my_qr_callback(qr_data: str):
        print("\nГенерация QR-кода...")
        qr = qrcode.QRCode()
        qr.add_data(qr_data)
        qr.print_ascii()  # Вывод QR-кода прямо в терминал
        print("\n⚠️  ВАЖНО: QR-код действителен только 2 минуты!")
        print("Отсканируйте этот код в мобильном приложении Госуслуги -> Сканер")
        print("(Ожидание сканирования...)\n")

    async with NetSchool(url) as ns:
        try:
            print("Запуск входа через QR-код Госуслуг...")

            # Запускаем вход. Библиотека сама будет ждать, пока вы отсканируете код.
            # Параметр school= нужен, если к аккаунту привязано несколько организаций.
            await ns.login_via_gosuslugi_qr(
                qr_callback=my_qr_callback,
                school=os.getenv("NS_SCHOOL"),
            )

            print("QR-код успешно отсканирован! Вход выполнен.")

            diary = await ns.diary()
            print(f"Дневник загружен: {len(diary.schedule)} дней.")

        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
