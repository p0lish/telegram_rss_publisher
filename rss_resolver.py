import feedparser
import time
import datetime
def resolve(url):
    return feedparser.parse(url)

def get_entries(url):
    return resolve(url)["entries"]

def list_entries(url):
    return [entry["title"] for entry in get_entries(url)]

def get_news_list(url):
    entries = get_entries(url)
    ordered_entries = sorted(entries, key=lambda entry: entry.published_parsed)
    return [{
        "title": entry.title,
        "timestamp": int(time.mktime(entry.published_parsed)),
        "url": entry.link
    } for entry in ordered_entries]


if __name__ == "__main__":
   print(get_news_list(URL))