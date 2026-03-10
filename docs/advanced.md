# Продвинутое использование

## Работа с вложениями (Attachments)

NetSchoolAPI часто содержит файлы, прикреплённые к домашним заданиям. Вложения находятся внутри заданий (`Assignment`), а задания — внутри уроков (`Lesson`).

```python
diary = await ns.diary()
for day in diary.schedule:
    for lesson in day.lessons:
        for assignment in lesson.assignments:
            if assignment.attachments:
                for attachment in assignment.attachments:
                    print(f"Найдено вложение: {attachment.name} (ID: {attachment.id})")
                    # Скачивание файла:
                    # from io import BytesIO
                    # buf = BytesIO()
                    # await ns.download_attachment(attachment.id, buf)
```

## Кастомные периоды

Вы можете запрашивать дневник не только на текущую неделю, но и на любой произвольный промежуток времени.

```python
import datetime

# Получить дневник за сентябрь
start = datetime.date(2025, 9, 1)
end = datetime.date(2025, 9, 30)

month_diary = await ns.diary(start=start, end=end)
print(f"Всего уроков за месяц: {sum(len(d.lessons) for d in month_diary.schedule)}")
```

## Работа с несколькими учениками (Родительский аккаунт)

*Функционал в разработке.* Если аккаунт является родительским и привязано несколько детей, API позволяет переключаться между ними.

## Средневзвешенный балл

Каждое задание имеет `weight` (вес/коэффициент). Контрольные обычно весят больше, чем домашние задания. Используйте это для точного подсчёта среднего балла:

```python
diary = await ns.diary(start=start, end=end)

marks = []
for day in diary.schedule:
    for lesson in day.lessons:
        for a in lesson.assignments:
            if a.mark:
                marks.append((a.mark, a.weight))

if marks:
    simple_avg = sum(m for m, _ in marks) / len(marks)
    weighted_sum = sum(m * w for m, w in marks)
    weight_total = sum(w for _, w in marks)
    weighted_avg = weighted_sum / weight_total

    print(f"Простой средний: {simple_avg:.2f}")
    print(f"Средневзвешенный: {weighted_avg:.2f}")
```

## Типы заданий

Каждое задание имеет поле `kind` (полное название типа) и `kind_abbr` (сокращение):

| Сокращение | Тип задания |
|---|---|
| О | Ответ на уроке |
| К | Контрольная работа |
| ДЗ | Домашнее задание |
| С | Самостоятельная работа |
| Т | Тестирование |
| Л | Лабораторная работа |
| П | Проект |
| Д | Диктант |
| Р | Реферат |
| Ч | Сочинение |
| И | Изложение |
| З | Зачёт |

```python
for day in diary.schedule:
    for lesson in day.lessons:
        for a in lesson.assignments:
            if a.mark:
                print(f"[{a.kind_abbr}] {a.kind}: {a.mark} (вес: {a.weight})")
```

## Внутренняя почта

Библиотека поддерживает внутреннюю почту «Сетевого Города».

### Список писем (реестр)

Получение списка писем с пагинацией. Поддерживаются папки:
`"Inbox"` (входящие), `"Sent"` (отправленные), `"Draft"` (черновики), `"Deleted"` (удалённые).

```python
# Первая страница входящих (20 писем)
page = await ns.mail_list("Inbox", page=1, page_size=20)
print(f"Всего писем: {page.total_items}, на странице: {len(page.entries)}")

for entry in page.entries:
    print(f"  #{entry.id}  {entry.sent}  {entry.author}  «{entry.subject}»")

# Вторая страница
if page.total_items > 20:
    page2 = await ns.mail_list("Inbox", page=2, page_size=20)

# Отправленные
sent = await ns.mail_list("Sent")
for entry in sent.entries:
    print(f"  #{entry.id}  «{entry.subject}»")
```

### Непрочитанные письма

```python
unread_ids = await ns.mail_unread()
print(f"Непрочитанных: {len(unread_ids)}")
```

### Чтение письма (текст + вложения)

```python
msg = await ns.mail_read(message_id)
print(f"От: {msg.author_name}")
print(f"Тема: {msg.subject}")
print(f"Текст: {msg.text}")
print(f"Дата: {msg.sent}")
print(f"Файлов: {len(msg.file_attachments)}")
```

### Скачивание вложений из письма

```python
from io import BytesIO

msg = await ns.mail_read(message_id)
for att in msg.file_attachments:
    buf = BytesIO()
    await ns.download_attachment(att.id, buf)
    with open(att.name, "wb") as f:
        f.write(buf.getvalue())
    print(f"Скачан: {att.name} ({len(buf.getvalue())} байт)")
```

### Список получателей

```python
recipients = await ns.mail_recipients()
for r in recipients:
    print(f"{r.name} ({r.organization_name})")
```

### Отправка письма

```python
recipients = await ns.mail_recipients()
await ns.mail_send(
    subject="Привет!",
    text="Текст письма.",
    to=[recipients[0].id],
)
```
