# NetschoolPy

**NetschoolPy** – это асинхронная библиотека для работы с электронным дневником «Сетевой город. Образование» (NetSchoolAPI).

Библиотека полностью переписана и оптимизирована для удобного использования в современных Python проектах. Поддерживает вход как по логину/паролю от школы, так и через **Госуслуги (ESIA)**.

## Установка

```bash
pip install netschoolpy
```

## Быстрый старт

```python
import asyncio
from netschoolpy import NetSchoolAPI

async def main():
    async with NetSchoolAPI('https://sgo.example.ru') as ns:
        await ns.login('login', 'password', 'Школа №1')
        
        diary = await ns.diary()
        for day in diary.schedule:
            for lesson in day.lessons:
                print(f"{lesson.number}. {lesson.subject}")

if __name__ == '__main__':
    asyncio.run(main())
```
