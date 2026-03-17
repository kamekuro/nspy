# Руководство пользователя

## Авторизация

Для работы с API необходимо авторизоваться. Поддерживается:
1.  Обычная авторизация (логин/пароль, выданные в школе).
2.  Авторизация через **Госуслуги (ESIA)** — логин/пароль или QR-код.

### Обычный вход

```python
from netschoolpy import NetSchoolAPI

async with NetSchoolAPI('https://your-netschool-url.ru') as ns:
    await ns.login('student_login', 'password', 'School Name')
```

### Вход через Госуслуги

Подробнее см. в разделе [Вход через Госуслуги](esia_login.md).

```python
await ns.login_via_gosuslugi(
    'gosuslugi_login',
    'gosuslugi_password',
    school='Школа №1',  # если привязано несколько организаций
)
```

Поддерживается SMS, TOTP и MAX (Госключ) как второй фактор — код запрашивается через `input()`.

### Вход через QR-код Госуслуг

Самый удобный способ — без ввода логина и пароля. Нужно отсканировать QR-код в мобильном приложении «Госуслуги».

```python
async def show_qr(qr_data: str):
    import qrcode
    qr = qrcode.QRCode()
    qr.add_data(qr_data)
    qr.print_ascii()
    print("⚠️  QR-код действителен 1 минуту!")
    print("Отсканируйте в приложении Госуслуги → Сканер")

await ns.login_via_gosuslugi_qr(qr_callback=show_qr, qr_timeout=120, school='Школа №1')
```

Подробнее: [Вход через Госуслуги](esia_login.md).

## Получение дневника

Основная функция – получение дневника.

```python
diary = await ns.diary()  # Текущая неделя
```

Можно указать конкретные даты:

```python
import datetime
start = datetime.date(2025, 9, 1)
end = datetime.date(2025, 9, 7)
diary = await ns.diary(start, end)
```

Дневник содержит список дней в поле `schedule`:

```python
for day in diary.schedule:
    print(f"Дата: {day.day}")
    for lesson in day.lessons:
        print(f"  {lesson.number}. {lesson.subject}")
        for assignment in lesson.assignments:
            if assignment.mark:
                print(f"     Оценка: {assignment.mark} (вес: {assignment.weight})")
                print(f"     Тип: {assignment.kind} [{assignment.kind_abbr}]")
```

## Обработка ошибок

Библиотека выбрасывает исключения в случае ошибок авторизации или сети.

```python
from netschoolpy import NetSchoolAPI
from netschoolpy.exceptions import LoginError, SchoolNotFound

try:
    await ns.login(...)
except LoginError:
    print("Ошибка входа")
except SchoolNotFound:
    print("Школа не найдена")
```

## Внутренняя почта

Библиотека поддерживает внутреннюю почту «Сетевого Города»:

```python
# Список писем (входящие, первая страница)
page = await ns.mail_list("Inbox", page=1, page_size=20)
print(f"Всего писем: {page.total_items}")
for entry in page.entries:
    print(f"  {entry.sent} | {entry.author} | {entry.subject}")

# Прочитать конкретное письмо (текст + вложения)
msg = await ns.mail_read(page.entries[0].id)
print(f"Текст: {msg.text}")

# Скачать вложения из письма
from io import BytesIO
for att in msg.file_attachments:
    buf = BytesIO()
    await ns.download_attachment(att.id, buf)
    with open(att.name, "wb") as f:
        f.write(buf.getvalue())
    print(f"Скачан: {att.name} ({len(buf.getvalue())} байт)")
```

Подробнее см. в [Продвинутое использование](advanced.md).
