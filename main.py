from rss_resolver import get_news_list
import pickle
import logging
from telegram.ext import Application
from dotenv import dotenv_values

config = dotenv_values('.env')


chat_id = config["CHAT_ID"]
interval = config["INTERVAL"]
URL = config["RSS_URL"]
filename = config["PICKLE_FILE"]
token = config["TOKEN"]

def if_file_exists(filename):
    try:
        with open(filename, "rb") as f:
            return True
    except FileNotFoundError:
        return False
def create_file_if_not_exists(filename):
    if not if_file_exists(filename):
        with open(filename, "wb") as f:
            pickle.dump([], f)

def save_news_list(news_list, filename):
    with open(filename, "wb") as f:
        pickle.dump(news_list, f)

def get_old_news_list(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

def compare_news_lists(news_list, old_news_list):
    return [news for news in news_list if news not in old_news_list]

async def send_news(context=None):
    news_list = get_news_list(URL)
    old_news_list = get_old_news_list(filename)
    newest_news = compare_news_lists(news_list, old_news_list)
    save_news_list(news_list, filename)

    for news in newest_news:
        url = news["url"]
        await context.bot.send_message(chat_id=chat_id, text=url)


if __name__ == "__main__":
    print(config)
    create_file_if_not_exists(filename) 
    application = Application.builder().token(token).build()
    jq = application.job_queue
    jq.run_repeating(send_news, interval=int(interval), first=1)
    
    application.run_polling()
