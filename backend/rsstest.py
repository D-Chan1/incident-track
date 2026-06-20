import feedparser
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
from zoneinfo import ZoneInfo
import psycopg2
import os
from dotenv import load_dotenv
from dotenv import find_dotenv
print(find_dotenv())
load_dotenv()

KEYWORDS = []

SUBREDDITS = [
    "https://www.reddit.com/r/polyphia/new/"
]

def iso_to_et(iso_time: str)->str:
    timestamp = datetime.fromisoformat(iso_time)
    return timestamp.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %I:%M %p %Z")

def extract_post_text(summary_html: str)->str:
    """Return a string that contains readable body text of a reddit post
    """
    soup = BeautifulSoup(summary_html, "html.parser") # soup becomes HTML that is easier to work with
    md_div = soup.find("div", class_="md") # reddit seems to use the md class for post bodies
    
    if md_div:
        return md_div.get_text(separator=" ").strip() # if the div exists, return the text in a readable format by separating the words with a space and strip extra space
    
    return ""  # div is None, meaning it's a post with no body text


def scrape_subreddit(url: str, key_words: list[str] )->list[dict]:
    """Return summaries of posts from given subreddit feed url filtered by key_words. 
    If key_words is empty, return all possible posts.

    Precondition: url must not be changed, url must be to a subreddit feed
    """

    url = url.rstrip("/") + "/.rss" # append .rss to the end to get readable rss of feed
    feed = feedparser.parse(url) # parse the rss

    results = []

    for entry in feed.entries: 
        # Strip HTML tags from body
        raw_html = str(entry.get("summary", "*No Body Text*"))
        # plain_text = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip() then i wouldn't need the helper function extract_post_text maybe?
        plain_text = extract_post_text(raw_html) # get the body text

        combined = (str(entry.get("title", "")) + " " + plain_text).lower() # make a string that combines the post title and body
        matched = [kw for kw in key_words if kw in combined] # ie. matched = [].  for kw in keywords, if kw in combined, matched.append(kw)

        post_info = {
                "id": entry.get("id", entry.link),
                "subreddit": "r/" + url.split("/r/")[1].split("/")[0],
                "title": entry.title,
                "text": plain_text,
                "url": entry.link,
                "author": entry.get('author', 'unknown'),
                "published": entry.published,
                "ET_time": iso_to_et(str(entry.published)),
                "matched_keywords": matched,
            }
        if not key_words or matched: # if we have titles+bodies that match keywords, add them to a list
            results.append(post_info)
    return results

# Test
all_posts = []
for url in SUBREDDITS:
    # go thru each subreddit, collect matched posts and add to list that contains posts from all subreddits
    posts = scrape_subreddit(url, KEYWORDS)
    all_posts.extend(posts)
    print(f"{url}: {len(posts)} matching posts found") 

for p in all_posts:
    print(f"\n[{', '.join(p['matched_keywords'])}] {p['subreddit']} {p['title']}")
    print(f"  by {p['author']} — {p['published']} - {p['ET_time']}")
    print(f"  {p['text'][:]}")
    print(f"  {p['url']}")

# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASS"),
# }
# DB_HOST = os.environ["DB_HOST"]
# DB_PORT = os.environ['DB_PORT']
# DB_NAME = os.environ['DB_NAME']
# DB_USER = os.environ['DB_USER']
# DB_PASS = os.environ['DB_PASS']


# def get_connection():
#     # return psycopg2.connect(**DB_CONFIG)
#      return psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS)
# def save_posts(conn, posts: list[dict]) -> int:
#     new_count = 0
#     with conn.cursor() as cur:
#         for post in posts:
#             cur.execute("""
#                 INSERT INTO posts
#                 (id, subreddit, title, text, url, author, published, matched_keywords)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                 ON CONFLICT (id) DO NOTHING
#             """, (
#                 post["id"], post["subreddit"], post["title"], post["text"],
#                 post["url"], post["author"], post["published"],
#                 post["matched_keywords"],
#             ))
#             if cur.rowcount > 0:
#                 new_count += 1
#     conn.commit()
#     return new_count

# conn = get_connection()
# new_count = save_posts(conn, all_posts)
# print(f"Saved {new_count} new posts to the database")
# conn.close()
# interesting_posts = []

# for post in feed.entries:
#     title = post.title.lower()

#     if any(word in title for word in KEYWORDS):
#         interesting_posts.append(post)

#         print("MATCH:", post.title)
#         print(post.link)
#         print()

# post1 = feed.entries[0]
# pprint(post1)
# for post in feed.entries:
#     print("TITLE:", post.title)
#     print("LINK:", post.link)
#     print("DATE:", post.published)
#     print("-" * 50)