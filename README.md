# tg-reader

MCP-сервер, через который AI-агент (Claude Code и т.п.) читает твой Telegram от твоего же
аккаунта (userbot, Telethon/MTProto) — но **только те чаты, что ты разрешил проекту**.

- Каждый проект подключает свой профиль — список чатов. Остальные чаты сервер не видит,
  не перечисляет и не отдаёт.
- Чтение, поиск, скачивание вложений — всегда. Отправка (`send_message`, `send_file`) — только
  если в профиле `write = true`.
- `send_file` берёт файлы только внутри `--upload-root` и никогда не шлёт скрытые пути
  (`.env`, `.ssh` …).
- Редактирования, удаления и отметки «прочитано» в коде нет.

## ⚠️ Прежде чем ставить

- Сессия Telegram (`TG_SESSION`) — это **полный доступ к твоему аккаунту**. Храни её как пароль:
  менеджер паролей или файл с правами `600`, никогда не в git и не в чат с агентом.
- Telegram не любит автоматизацию пользовательских аккаунтов. Читай умеренно; теоретически
  аккаунт могут ограничить.
- Отозвать доступ: Telegram → Настройки → Устройства → завершить сессию.

## Установка

```bash
git clone <repo> ~/tg-reader && cd ~/tg-reader
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

1. **API-ключи.** <https://my.telegram.org/apps> → создать приложение → `api_id` и `api_hash`.
2. **Вход** (QR-код в терминале; `--phone` — вход по коду из Telegram):

   ```bash
   export TG_API_ID=... TG_API_HASH=...
   mkdir -p ~/.config/tg-reader
   (umask 077; .venv/bin/python -m tg_reader.login --raw > ~/.config/tg-reader/session)
   ```

   Строка сессии попадает только в файл, на экран не выводится.
3. **Найти чаты:** `TG_SESSION_FILE=~/.config/tg-reader/session .venv/bin/python -m tg_reader.chats "часть названия"`
   печатает `id<TAB>тип<TAB>название`.
4. **Профиль:** `cp profiles.example.toml profiles.toml`, вписать id нужных чатов.

## Подключение к проекту

`.mcp.json` в корне проекта (пути — свои):

```json
{
  "mcpServers": {
    "telegram": {
      "command": "/home/me/tg-reader/.venv/bin/python",
      "args": [
        "-m", "tg_reader.server",
        "--profile", "myproject",
        "--download-dir", "/home/me/projects/myproject/tg-files"
      ],
      "env": {
        "PYTHONPATH": "/home/me/tg-reader",
        "TG_API_ID": "123456",
        "TG_API_HASH": "${TG_API_HASH}",
        "TG_SESSION_FILE": "/home/me/.config/tg-reader/session"
      }
    }
  }
}
```

- `TG_API_HASH` лучше держать в окружении шелла (`${...}` Claude Code подставит сам),
  чем писать в `.mcp.json`, если проект в git.
- `--upload-root <dir>` включает `send_file` (и только если `write = true`).
- `tg-files/` добавь в `.gitignore` проекта.
- Новый чат в `profiles.toml` подхватывается после перезапуска сервера (новая сессия агента).

## Переменные

| Env               | Что                                                   |
| ----------------- | ----------------------------------------------------- |
| `TG_API_ID`       | api_id с my.telegram.org                              |
| `TG_API_HASH`     | api_hash оттуда же                                    |
| `TG_SESSION`      | строка сессии (или вместо неё ↓)                      |
| `TG_SESSION_FILE` | путь к файлу со строкой сессии                        |

Как есть, без гарантий.
