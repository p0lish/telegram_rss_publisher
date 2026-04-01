import json
import logging
from pathlib import Path
from telegram.ext import Application
from dotenv import dotenv_values
from rss_resolver import get_news_list

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

config = dotenv_values(".env")

CHAT_ID = config["CHAT_ID"]
INTERVAL = int(config["INTERVAL"])
RSS_URL = config["RSS_URL"]
TOKEN = config["TOKEN"]
STATE_FILE = Path(config.get("STATE_FILE", "seen.json"))


def load_seen() -> set:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            return set(data)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Corrupt state file, starting fresh")
    return set()


def save_seen(seen: set):
    STATE_FILE.write_text(json.dumps(list(seen)))


async def send_news(context=None):
    try:
        news_list = get_news_list(RSS_URL)
    except Exception as e:
        logger.error(f"Failed to fetch RSS: {e}")
        return

    seen = load_seen()
    new_articles = [n for n in news_list if n["url"] not in seen]

    if not new_articles:
        logger.info("No new articles")
        return

    logger.info(f"{len(new_articles)} new article(s)")

    for article in new_articles:
        tags = article["tags"]
        text = article["url"]
        if tags:
            text += f"\n{tags}"

        try:
            await context.bot.send_message(chat_id=CHAT_ID, text=text)
            seen.add(article["url"])
            logger.info(f"Sent: {article['title']}")
        except Exception as e:
            logger.error(f"Failed to send '{article['title']}': {e}")

    save_seen(seen)


if __name__ == "__main__":
    # Migrate pickle state if it exists
    pickle_file = Path("telex_seen.pkl")
    if pickle_file.exists() and not STATE_FILE.exists():
        try:
            import pickle
            with open(pickle_file, "rb") as f:
                old_data = pickle.load(f)
            urls = {item["url"] for item in old_data if isinstance(item, dict) and "url" in item}
            save_seen(urls)
            logger.info(f"Migrated {len(urls)} URLs from pickle to JSON")
        except Exception as e:
            logger.warning(f"Could not migrate pickle: {e}")

    logger.info(f"Starting telexbot — checking {RSS_URL} every {INTERVAL}s")
    application = Application.builder().token(TOKEN).build()
    jq = application.job_queue
    jq.run_repeating(send_news, interval=INTERVAL, first=5)
    application.run_polling()
