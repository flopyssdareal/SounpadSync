# 🎧 SoundpadSync

**Telegram-бот + десктоп-приложение для автоматической загрузки звуков из TikTok/YouTube Shorts прямо в [Soundpad](https://www.leppsoft.com/soundpad/).**

Скинул ссылку в Telegram → бот скачал аудио → ты подтвердил в приложении → трек сам появился в Soundpad, в нужной категории. Без ручного скачивания, конвертации и перетаскивания файлов.

![Python](https://img.shields.io/badge/python-3.13-blue)
![Platform](https://img.shields.io/badge/platform-Windows-informational)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Возможности

- 🤖 **Telegram-бот** принимает ссылки на TikTok / YouTube Shorts и скачивает из них аудиодорожку (`yt-dlp` + `ffmpeg`).
- 🎚️ **Очередь на модерацию** — каждый скачанный трек попадает в очередь в GUI, где можно прослушать, переименовать, выбрать категорию и подтвердить или отклонить.
- 🏷️ **Автоопределение категории** по ключевым словам в описании видео (мемы, музыка, аниме, игры, фильмы и т.д.) — категорию всегда можно поменять вручную перед подтверждением.
- 🔌 **Прямая интеграция с Soundpad** через официальный Remote Control API (Named Pipe) — трек добавляется в программу автоматически, без импорта файлов руками.
- 🔁 **Автосинхронизация** — можно включить периодическую проверку и обработку очереди по расписанию.
- 🌍 **Локализация** — интерфейс на русском и английском.
- 🖥️ **Понятный первичный визард** — настройка языка и токена бота при первом запуске.
- 📋 **Логи и диагностика** — встроенное окно логов и самотестирование подключения к Soundpad (проверка процесса, пайпа, версии API).

## 🖼️ Как это работает

```
Telegram → бот скачивает аудио (yt-dlp) → сохраняет во временную папку
        → очередь на модерацию в GUI → подтверждение категории/названия
        → перемещение файла в папку категории → DoAddSound() через Soundpad Remote Control API
```

## 📦 Требования

- Windows 10/11
- [Soundpad](https://www.leppsoft.com/soundpad/) с включённым **Remote Control API** (`Файл → Настройки → Удалённое управление`)
- Python 3.13+ (если запускаете из исходников)
- `ffmpeg.exe` и `ffprobe.exe` в папке проекта
- Токен Telegram-бота ([@BotFather](https://t.me/BotFather))

## 🚀 Установка и запуск

### Из исходников

```bash
git clone https://github.com/flopyssdareal/SoundpadSync.git
cd SoundpadSync
pip install -r requirements.txt
python main.py
```

При первом запуске откроется мастер первоначальной настройки — выберите язык и вставьте токен бота.

### Готовый .exe

Скачайте `SoundpadSync.exe` из [Releases](../../releases), положите рядом `ffmpeg.exe` и `ffprobe.exe`, запустите.

## ⚙️ Сборка exe самостоятельно

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name SoundpadSync ^
  --icon=icon.ico --add-data "icon.ico;." ^
  --collect-all customtkinter ^
  --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." ^
  main.py
```

## 🛠️ Настройка Soundpad

1. Откройте Soundpad → `Файл → Настройки → Разработчикам` → включите **Enable developer API**.
2. Там же, во вкладке **Remote Control**, включите удалённое управление.
3. Если Soundpad запущен от имени администратора — SoundpadSync тоже нужно запускать от администратора (иначе Windows не даст открыть канал между процессами с разными правами).

## 🧩 Стек технологий

| Компонент | Технология |
|---|---|
| GUI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Telegram-бот | [aiogram](https://github.com/aiogram/aiogram) |
| Загрузка видео | [yt-dlp](https://github.com/yt-dlp/yt-dlp) + ffmpeg |
| Хранилище | SQLite |
| Интеграция с Soundpad | [Remote Control API](https://www.leppsoft.com/soundpad/help/manual/tutorial/rc/) через Named Pipe |

## 📁 Структура проекта

```
SoundpadSync/
├── main.py                 # точка входа, логирование, запуск GUI + бота
├── modules/
│   ├── gui_app.py           # интерфейс на CustomTkinter
│   ├── bot_manager.py        # Telegram-бот, скачивание и обработка видео
│   ├── db_manager.py          # работа с SQLite (очередь, настройки)
│   └── spl_manager.py           # интеграция с Soundpad Remote Control API
├── ffmpeg.exe / ffprobe.exe
└── icon.ico
```

## ❓ FAQ / Troubleshooting

**"Pipe not found / Error 2"** — Soundpad не запущен, либо не включён Remote Control API, либо приложение запущено без прав администратора, а Soundpad — с ними (см. раздел «Настройка Soundpad» выше).

**"R-204: File does not exist"**, хотя файл на месте — обычно возникает из-за кириллицы в пути на не-русской кодовой странице системы; исправлено в текущей версии за счёт корректной ANSI-кодировки команд.

**Бот скачал файл, но он не появляется в очереди** — проверьте окно логов в приложении (`Логи и диагностика`) на наличие ошибок yt-dlp/ffmpeg.

## 📄 Лицензия

MIT — делайте с кодом что хотите, но без каких-либо гарантий.

## 🤝 Вклад

Issues и Pull Request'ы приветствуются. Перед крупными изменениями лучше сначала открыть issue, чтобы обсудить подход.
