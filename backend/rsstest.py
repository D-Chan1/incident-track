import feedparser
import requests
from bs4 import BeautifulSoup
from pprint import pprint

KEYWORDS = ["girl","black", "feel"]

feed_url = "https://www.reddit.com/r/polyphia/new/.rss"



SUBREDDITS = [
    "https://www.reddit.com/r/polyphia/new/.rss"
]
def extract_post_text(summary_html):
    soup = BeautifulSoup(summary_html, "html.parser")
    md_div = soup.find("div", class_="md")
    if md_div:
        return md_div.get_text(separator=" ").strip()
    return ""  # link post with no body text


def scrape_subreddit(url):
    feed = feedparser.parse(url)
    results = []

    for entry in feed.entries:
        print("TITLE:", entry.title)
        print("SUMMARY LENGTH:", len(entry.get("summary", "")))
        print("SUMMARY:", entry.get("summary", "")[:500])
        print("---")

        # Strip HTML tags from body
        raw_html = entry.get("summary", "")
        # plain_text = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()
        plain_text = extract_post_text(raw_html)

        combined = (entry.title + " " + plain_text).lower()
        matched = [kw for kw in KEYWORDS if kw in combined]

        if matched:
            results.append({
                "title": entry.title,
                "text": plain_text,
                "url": entry.link,
                "author": entry.author,
                "published": entry.published,
                "matched_keywords": matched,
            })

    return results

# Test
all_posts = []
for url in SUBREDDITS:
    posts = scrape_subreddit(url)
    all_posts.extend(posts)
    print(f"{url}: {len(posts)} matching posts found")

for p in all_posts:
    print(f"\n[{', '.join(p['matched_keywords'])}] {p['title']}")
    print(f"  by {p['author']} — {p['published']}")
    print(f"  {p['text'][:]}")
    print(f"  {p['url']}")



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