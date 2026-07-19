import psycopg2
from backend.app.database import SessionLocal
from backend.app.models import Post, Test
from backend.app.services.reddit import iso_to_et, extract_post_text, scrape_subreddit, create_post_from_dict, add_post

KEYWORDS = ['lasers']

SUBREDDITS = [
    "https://www.reddit.com/r/polyphia/new/"
]


all_posts = []

# print all matching post in summary form
for url in SUBREDDITS:
    # go thru each subreddit, collect matched posts and add to list that contains posts from all subreddits
    posts = scrape_subreddit(url, KEYWORDS)
    all_posts.extend(posts)
    print(f"{url}: {len(posts)} matching posts found") 


testdic = all_posts[0]
print(testdic)


print("\n --------ALL POSTS MATCHED-------\n ")
for p in all_posts:
    print(f"\n[{', '.join(p['matched_keywords'])}] {p['subreddit']} {p['title']}")
    print(f"  by {p['author']} — {p['published']} - {p['ET_time']}")
    print(f"  {p['body'][:]}")
    print(f"  {p['url']}")


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




