import os
from langchain_openai import OpenAIEmbeddings
from models.database import SessionLocal
from models.blog_article import BlogArticle
from sqlalchemy import text
from dotenv import load_dotenv
import numpy as np

def find_similar_article():
    # Load environment variables
    load_dotenv()
    
    # Initialize the embeddings model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Get user input
    user_input = input("Enter your search text: ")
    
    # Create embedding for user input
    input_embedding = embeddings.embed_query(user_input)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Convert the embedding to a string representation for PostgreSQL
        embedding_str = ','.join(map(str, input_embedding))
        
        # Query to find the most similar article using cosine similarity
        # We'll search in both content and summary embeddings
        query = text(f"""
            SELECT 
                id, 
                title, 
                url, 
                date, 
                content, 
                summary,
                (content_embedding <=> ARRAY[{embedding_str}]::vector) as content_similarity,
                (summary_embedding <=> ARRAY[{embedding_str}]::vector) as summary_similarity
            FROM 
                blog_articles
            ORDER BY 
                LEAST((content_embedding <=> ARRAY[{embedding_str}]::vector), (summary_embedding <=> ARRAY[{embedding_str}]::vector))
            LIMIT 1
        """)
        
        # Execute the query
        result = db.execute(query).fetchone()
        
        if result:
            print("\n=== Most Similar Article ===")
            print(f"Title: {result.title}")
            print(f"Date: {result.date}")
            print(f"URL: {result.url}")
            print(f"Content Similarity: {1 - result.content_similarity:.4f}")
            print(f"Summary Similarity: {1 - result.summary_similarity:.4f}")
            print("\n=== Summary ===")
            print(result.summary)
            print("\n=== Full Content ===")
            print(result.content)
        else:
            print("No articles found in the database.")
    
    except Exception as e:
        print(f"Error finding similar article: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    find_similar_article() 