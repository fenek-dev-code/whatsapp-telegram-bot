# WhatsApp Parser Integrated Telegram Bot 🚀

![Меме](https://img-webcalypt.ru/uploads/admin/images/meme-templates/vBTD9cBjZurckxkYtl4plerdMBVotX79.jpg)

Этот проект представляет собой интегрированное решение, объединяющее Telegram бота с парсером WhatsApp для автоматизации работы с сообщениями и платежами.

## 📋 Предварительные требования

1. **Python 3.10+** - [Скачать Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Скачать Node.js](https://nodejs.org/)
3. **Git** - [Скачать Git](https://git-scm.com/)

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/whatsapp-telegram-bot.git
cd whatsapp-telegram-bot
```

### 2. Настройка окружения

Перейдите в директорию Telegram бота:
```bash
cd ./telegram_bot
```

Создайте файл `.env` на основе примера:
```bash
cp .exemple.env .env
```

Отредактируйте файл `.env`:
```ini
# ===== Telegram Bot Settings =====
BOT_TOKEN=ваш_токен_бота
BOT_ADMIN_CHANNEL_ID=-1001234567890
ADMINS_LIST=123456789,987654321
FQA_LINK=https://t.me/your_faq_channel

# ===== Payment Settings =====
AAIO_SHOP_ID=ваш_shop_id
AAIO_API_KEY=ваш_api_key
AAIO_SECRET_KEY=ваш_secret_key
MIN_DEPOSIT=100
MAX_DEPOSIT=10000

# ===== API Settings =====
API_HOST=0.0.0.0
API_PORT=3000
```

### 3. Установка зависимостей для Telegram бота

Установите `uv` - современный менеджер зависимостей Python:
```bash
pip install uv
```

Синхронизируйте зависимости:
```bash
uv sync
```

### 4. Запуск Telegram бота
```bash
uv run main.py
```

## 🔌 Настройка WhatsApp парсера

### 1. Перейдите в директорию парсера
```bash
cd ../whats_app_parse
```

### 2. Установите зависимости
```bash
npm install
```

### 3. Запустите парсер
```bash
npm run run
```

### 4. Сканируйте QR-код
Откройте WhatsApp на своем телефоне:
1. Перейдите в Настройки → WhatsApp Web/Свяжите устройство
2. Отсканируйте QR-код из терминала

### 5. Получите ID чатов
В нужных чатах WhatsApp отправьте команду:
```
!chat_id
```

Добавьте полученные ID в файл `.env` в раздел `WHATSAPP_ALLOWED_CHATS`.

## 🧩 Структура проекта

```
whatsapp-telegram-bot/
├── parse_bot/
│   ├── telegram_bot/
│   │   ├── .env              # Конфигурация бота
│   │   ├── main.py           # Основной код бота
│   │   └── ...
│   └── whats_app_parse/
│       ├── main.js           # Код парсера WhatsApp
│       └── ...
├── .gitignore
└── README.md
```

## ⚙️ Основные команды управления

| Команда | Описание |
|---------|----------|
| `uv run main.py` | Запуск Telegram бота |
| `npm run run` | Запуск WhatsApp парсера |
| `uv sync` | Обновление Python зависимостей |
---

**Теперь ваш бот полностью настроен и готов к работе!** 🎉
