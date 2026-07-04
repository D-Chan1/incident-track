import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import psycopg2
from app.database import SessionLocal
from app.models import Post, Test
from app.services.reddit import add_post

KEYWORDS = ['milan']

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
    """Return list of dict info of posts from given subreddit feed url filtered by key_words. 
    If key_words is empty, return all possible posts.

    Precondition: url must not be changed, url must be to a subreddit feed
    """

    url = url.rstrip("/") + "/.rss" # append .rss to the end to get readable rss of feed
    feed = feedparser.parse(url) # parse the rss

    results = []

    for entry in feed.entries: 
        # Strip HTML tags from body
        raw_html = str(entry.get("summary", ""))
        # plain_text = BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip() then i wouldn't need the helper function extract_post_text maybe?
        plain_text = extract_post_text(raw_html) # get the body text

        combined = (str(entry.get("title", "")) + " " + plain_text).lower() # make a string that combines the post title and body
        matched = [kw for kw in key_words if kw in combined] # ie. matched = [].  for kw in keywords, if kw in combined, matched.append(kw)

        post_info = {
                "id": str(entry.get("id")).split('/')[-1],
                "title": entry.title,
                "body": plain_text,
                "url": entry.link,
                "subreddit": "r/" + url.split("/r/")[1].split("/")[0],
                "author": entry.get('author', 'unknown'),
                "published": entry.published,
                "ET_time": iso_to_et(str(entry.published)),
                "matched_keywords": matched,
            }
        if not key_words or matched: # if we have titles+bodies that match keywords, add them to a list
            results.append(post_info)
    return results

# print all matching post in summary form
all_posts = []
for url in SUBREDDITS:
    # go thru each subreddit, collect matched posts and add to list that contains posts from all subreddits
    posts = scrape_subreddit(url, KEYWORDS)
    all_posts.extend(posts)
    print(f"{url}: {len(posts)} matching posts found") 


testdic = all_posts[0]
print(testdic)

# create Post object for insertion into Post table with post info as dictionariy
def create_post_from_dict(post_dict: dict):
    post = Post(id=post_dict['id'], title=post_dict['title'], body=post_dict['body']
                , url=post_dict['url'], subreddit=post_dict['subreddit'], author=post_dict['author'], published=datetime.fromisoformat(post_dict['published'])
    )

    return post



# post object to test inserion
testpost = create_post_from_dict(testdic)

with SessionLocal() as db:
    saved = 0
    skipped = 0
    for post_dict in all_posts:
        post = create_post_from_dict(post_dict)
        if add_post(db, post):
            saved+=1
        else:
            skipped+=1
    db.commit()
    

print('\n\n')


# test to see if insertion worked, currently doesn't work if running rsstest.py in terminal
# retrieved = db.query(Post).all()
# print(retrieved)

# print("\n --------ALL POSTS-------\n ---------\n")
# for p in all_posts:
#     print(f"\n[{', '.join(p['matched_keywords'])}] {p['subreddit']} {p['title']}")
#     print(f"  by {p['author']} — {p['published']} - {p['ET_time']}")
#     print(f"  {p['body'][:]}")
#     print(f"  {p['url']}")

