from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, Table, Column, ForeignKey#, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base

# creates incidents table
class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

post_keywords = Table(
    "post_keywords", Base.metadata,
    Column(
        'post_id', ForeignKey('posts.id'), primary_key=True
    ),
    Column(
        'keyword_id', ForeignKey('keywords.id'), primary_key=True
    )
)
class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str | None] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(String, index=True)
    subreddit: Mapped[str] = mapped_column(String, index=True)
    author: Mapped[str] = mapped_column(String)
    published: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    # keywords: Mapped[ARRAY]= mapped_column(ARRAY)
    # keywords = relationship("Keyword", secondary=post_keywords, back_populates = 'posts')
 

class Keyword(Base):
    __tablename__ = 'keywords'

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(unique=True, index=True)

    # posts = relationship("Post", secondary=post_keywords, back_populates='keywords')