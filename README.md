# Telegram RSS Publisher

A lightweight Python bot that monitors an RSS feed and publishes new articles to a Telegram channel or chat.

## Features

- Polls any RSS feed at a configurable interval
- Extracts rich tags from article meta keywords (falls back to RSS category tags)
- Deduplicates articles using a local JSON state file
- Clean message format — URL + tags, lets Telegram's link preview handle the rest
- Error handling with graceful fallbacks (no crashes on feed downtime)

## Setup

### Requirements

- Python 3.10+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure

Create a `.env` file:

```env
TOKEN=your-telegram-bot-token
CHAT_ID=-100xxxxxxxxxx
RSS_URL=https://example.com/rss
INTERVAL=300
STATE_FILE=seen.json
```

| Variable | Description |
|----------|-------------|
| `TOKEN` | Telegram bot API token |
| `CHAT_ID` | Target chat/channel ID (use `-100` prefix for channels) |
| `RSS_URL` | RSS feed URL to monitor |
| `INTERVAL` | Polling interval in seconds (default: 300) |
| `STATE_FILE` | Path to the JSON state file (default: `seen.json`) |

### Run

```bash
python3 main.py
```

### Run as a systemd service

```ini
[Unit]
Description=Telegram RSS Publisher
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/telegram_rss_publisher
EnvironmentFile=/path/to/telegram_rss_publisher/.env
ExecStart=/usr/bin/python3 main.py
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
```

## License

MIT
