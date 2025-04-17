import json
import os
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

def create_embeddings():
    # Initialize the embeddings model
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Create embeddings directory if it doesn't exist
    embeddings_dir = Path("blog_articles_embeddings")
    embeddings_dir.mkdir(exist_ok=True)

    # Read the source JSON file
    source_file = Path("blog_articles/vfb_articles_20250414_193539.json")
    with open(source_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    # Process each article and create embeddings
    for article in articles:
        # Generate embeddings for title and content
        title_embedding = embeddings.embed_query(article['full_title'])
        content_embedding = embeddings.embed_query(article['content'])

        # Add embeddings to the article data
        article['embedding_full_title'] = title_embedding
        article['embedding_content'] = content_embedding

    # Save the enhanced articles to a new JSON file
    output_file = embeddings_dir / "vfb_articles_with_embeddings.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    print(f"Embeddings created and saved to {output_file}")

if __name__ == "__main__":
    create_embeddings() 