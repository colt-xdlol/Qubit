<div align="center">

# ⚛️ Qubit

### AI Telegram Bot powered by RouterAI & Aiogram 3

Быстрый и современный Telegram-бот с поддержкой ИИ, системой лимитов, админ-панелью и монетизацией через YooMoney.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-v3-success?style=for-the-badge)
![RouterAI](https://img.shields.io/badge/RouterAI-AI-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-GPL--3.0-red?style=for-the-badge)

</div>

---

## ✨ Возможности

- 🤖 Интеграция с RouterAI
- ⚡ Высокая скорость ответов
- 👤 Личный кабинет пользователя
- 🛡️ Система банов и ограничений
- 🎁 Бесплатные ежедневные запросы
- 💎 Премиум-доступ
- 💳 YooMoney платежи
- 📊 Административная панель
- 🗄️ Работа с базой данных
- 🔄 Middleware архитектура
- 🧩 FSM состояния Aiogram 3

---

## 📂 Структура проекта

```text
Qubit/
│
├── admin/                # Админ-панель
├── config/               # Конфигурация
├── data/                 # Данные проекта
├── database/             # Работа с БД
├── handlers/             # Пользовательские хендлеры
├── keyboards/            # Клавиатуры
├── middlewares/          # Middleware
├── services/             # Сервисы (RouterAI, YooMoney и др.)
├── states/               # FSM состояния
│
├── main.py               # Точка входа
└── requirements.txt
```

---

## 🚀 Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/colt-xdlol/Qubit.git
cd Qubit
```

### 2. Создать виртуальное окружение

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## ⚙️ Настройка

Создайте файл `.env`

```env
BOT_TOKEN=your_bot_token

ROUTERAI_API_KEY=your_routerai_api_key
ROUTERAI_BASE_URL=https://openai.routerai.com/v1
ROUTERAI_MODEL=gpt-4o-mini

YOOMONEY_TOKEN=your_yoomoney_token

ADMIN_IDS=123456789
```

---

## ▶️ Запуск

```bash
python main.py
```

---

## 🧠 Используемые технологии

| Технология | Назначение |
|------------|------------|
| Aiogram 3 | Telegram Bot Framework |
| RouterAI API | Искусственный интеллект |
| SQLite/PostgreSQL | Хранение данных |
| YooMoney | Приём платежей |
| Python 3.11+ | Основной язык |

---

## 🔒 Безопасность

- Middleware-защита пользователей
- Система блокировок
- Ограничение бесплатных запросов
- Контроль доступа администратора

---

## 📈 Roadmap

- [ ] Поддержка нескольких моделей
- [ ] История диалогов
- [ ] Реферальная система
- [ ] Веб-панель администратора
- [ ] Статистика пользователей
- [ ] Поддержка нескольких провайдеров

---

## 🤝 Контрибьютинг

Pull Requests приветствуются.

Для крупных изменений сначала откройте Issue для обсуждения.

---

## 📜 Лицензия

Проект распространяется под лицензией **GPL-3.0**.

---

<div align="center">

### ⚛️ Qubit

Fast • Smart • Modern

Made with ❤️ by Amaral

</div>
