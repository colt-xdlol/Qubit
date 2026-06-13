<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=200&color=0:6a11cb,100:2575fc&text=Qubit&fontAlignY=40&fontSize=60&fontColor=ffffff&desc=AI%20Telegram%20Bot%20—%20Powered%20by%20RouterAI&descAlignY=56&descSize=16"/>
</div>

<p align="center">
  <b>Qubit</b> — современный Telegram-бот с искусственным интеллектом.<br>
  Быстрые ответы, система лимитов, реферальная программа и встроенные платежи.
</p>

<p align="center">
  <a href="#🚀-быстрый-старт"><kbd>🚀 Быстрый старт</kbd></a>
  ·
  <a href="#✨-возможности"><kbd>✨ Возможности</kbd></a>
  ·
  <a href="#⚙️-конфигурация"><kbd>⚙️ Конфигурация</kbd></a>
  ·
  <a href="#🧠-архитектура"><kbd>🧠 Архитектура</kbd></a>
  ·
  <a href="#📜-лицензия"><kbd>📜 Лицензия</kbd></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Aiogram_3-0099CC?style=flat-square&logo=telegram&logoColor=white" alt="Aiogram">
  <img src="https://img.shields.io/badge/RouterAI-FF6B35?style=flat-square&logo=openai&logoColor=white" alt="RouterAI">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/License-GPL_3.0-red?style=flat-square" alt="License">
</p>

<br>

---

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Токен бота от [@BotFather](https://t.me/BotFather)
- API-ключ [RouterAI](https://routerai.io)

### Установка за 3 шага

```bash
# 1. Клонировать
git clone https://github.com/colt-xdlol/Qubit.git
cd Qubit

# 2. Виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Установка
pip install -r requirements.txt
```

### Конфигурация

```bash
cp .env.example .env
```

<details open>
<summary><b>📝 Параметры .env</b></summary>

| Переменная | Обязательный | По умолчанию | Описание |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Токен Telegram бота |
| `ROUTERAI_API_KEY` | ✅ | — | API-ключ RouterAI |
| `ROUTERAI_BASE_URL` | ❌ | `https://api.routerai.io/v1` | Базовый URL OpenAI-совместимого API |
| `ROUTERAI_MODEL` | ❌ | `deepseek/deepseek-v4-flash` | Название модели |
| `ADMIN_IDS` | ❌ | `""` | ID администраторов через запятую |
| `DAILY_FREE_LIMIT` | ❌ | `10` | Бесплатных запросов в день |
| `SUPPORT_USERNAME` | ❌ | `"megasoki"` | Username поддержки без @ |
| `YOOMONEY_WALLET` | ❌ | `""` | Номер кошелька ЮMoney |
| `PRICE_PER_REQUEST_STARS` | ❌ | `10` | Цена запроса в Telegram Stars |
| `PUBLIC_BASE_URL` | ❌ | `""` | Публичный URL для вебхуков |

</details>

### Запуск

```bash
python main.py
```

---

## ✨ Возможности

<table>
  <tr>
    <td align="center" width="33%">
      <h3>🧠 RouterAI</h3>
      <p>Поддержка любой OpenAI-совместимой модели через RouterAI. DeepSeek, GPT, Claude и другие</p>
    </td>
    <td align="center" width="33%">
      <h3>📊 Лимиты</h3>
      <p>Ежедневная квота с автопродлением. Покупка дополнительных запросов через Telegram Stars или ЮMoney</p>
    </td>
    <td align="center" width="33%">
      <h3>👥 Рефералы</h3>
      <p>Уникальная ссылка для каждого пользователя. +1 к лимиту за каждого приглашённого навсегда</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <h3>🛡️ Админ-панель</h3>
      <p>Управление пользователями, рассылки, модерация. Business Connect для бизнес-аккаунтов</p>
    </td>
    <td align="center" width="33%">
      <h3>💬 Контекст диалога</h3>
      <p>Краткосрочная память: бот помнит историю сообщений и отвечает с учётом контекста</p>
    </td>
    <td align="center" width="33%">
      <h3>⚡ Скорость</h3>
      <p>Асинхронная архитектура на Aiogram 3. Мгновенные ответы без задержек</p>
    </td>
  </tr>
</table>

---

## 🧠 Архитектура

```
Qubit/
├── admin/              # Административная панель
├── config/             # Pydantic-конфигурация
├── data/               # SQLite база данных
├── database/           # Слой работы с БД
├── handlers/           # Обработчики команд и callback'ов
├── keyboards/          # Inline-клавиатуры
├── middlewares/        # Middleware (баны, инъекции)
├── services/           # Бизнес-логика (RouterAI, платежи, квота)
├── states/             # FSM состояния
├── assets/             # Медиа-файлы
├── main.py             # Точка входа
└── requirements.txt
```

### Поток запроса

```
User → Telegram → Aiogram Router → Middleware (ban/inject) → Handler
                                                              ↓
                                                    RouterAI Service → OpenAI-compatible API
                                                              ↓
                                                    Database (memory/quota) → Response → User
```

---

## 📦 Зависимости

| Пакет | Версия | Назначение |
|---|---|---|
| `aiogram` | ≥3.14 | Telegram Bot Framework нового поколения |
| `openai` | ≥1.55 | Клиент для OpenAI/RouterAI API |
| `aiosqlite` | ≥0.20 | Асинхронная работа с SQLite |
| `pydantic-settings` | ≥2.6 | Валидация конфигурации из .env |
| `aiohttp` | ≥3.9 | Асинхронные HTTP-запросы |

---

## 🤝 Контрибьютинг

1. Fork репозитория
2. Создайте ветку: `git checkout -b feature/my-feature`
3. Внесите изменения и закоммитьте: `git commit -m 'feat: add my feature'`
4. Отправьте в свой fork: `git push origin feature/my-feature`
5. Откройте Pull Request

> Для крупных изменений сначала откройте Issue для обсуждения.

---

## 📜 Лицензия

Проект распространяется под лицензией **GNU GPL v3**. Подробнее — в файле [LICENSE](LICENSE).

---

<div align="center">
  <br>
  <img src="https://capsule-render.vercel.app/api?type=waving&height=100&color=0:6a11cb,100:2575fc&section=footer"/>
  <br><br>
  <p>
    <b>⚛️ Qubit</b> — Fast • Smart • Modern
  </p>
  <p>
    Made with ❤️ by Amaral &nbsp;·&nbsp;
    <a href="https://github.com/colt-xdlol/Qubit">GitHub</a>
  </p>
</div>