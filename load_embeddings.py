import json
import os
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from models.database import SessionLocal
from models.blog_article import BlogArticle
from dotenv import load_dotenv

def load_embeddings():
    # Load environment variables
    load_dotenv()
    
    # Initialize the embeddings model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Read the source JSON file
    source_file = "blog_articles/vfb_articles_20250414_193539.json"
    with open(source_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Process each article
        for article in articles:
            # Generate embeddings for content and summary
            content_embedding = embeddings.embed_query(article['content'])
            summary_embedding = embeddings.embed_query(article['summary'])
            
            # Parse the date string to datetime object
            # The date format is like "Club, 14. April 2025"
            date_str = article['date'].split(', ')[1]  # Get "14. April 2025"
            date_obj = datetime.strptime(date_str, '%d. %B %Y')
            
            # Create a new BlogArticle instance
            blog_article = BlogArticle(
                title=article['title'],
                url=article['url'],
                date=date_obj,
                content=article['content'],
                summary=article['summary'],
                content_embedding=content_embedding,
                summary_embedding=summary_embedding
            )
            
            # Add to database
            db.add(blog_article)
        
        # Commit all changes
        db.commit()
        print(f"Successfully loaded {len(articles)} articles with embeddings into the database")
        
    except Exception as e:
        print(f"Error loading embeddings: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    load_embeddings() 