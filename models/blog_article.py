from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from .database import Base

class BlogArticle(Base):
    __tablename__ = 'blog_articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)
    date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    content_embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions
    summary_embedding = Column(Vector(1536))

    def __repr__(self):
        return f"<BlogArticle(title='{self.title}', url='{self.url}', date='{self.date}')>" 