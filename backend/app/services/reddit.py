from app.models import Post
from sqlalchemy import select 


def add_post(db, post: Post)->Post | None:
    existing = db.scalars(select(Post).where(Post.id == post.id)).first()
    if existing:
        return None
    
    db.add(post) 
    return post



    