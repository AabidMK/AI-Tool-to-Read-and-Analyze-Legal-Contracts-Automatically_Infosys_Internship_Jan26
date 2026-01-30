from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"


def embed_text(text: str) -> list[float]:
    """
    Converts input text into a vector embedding.
    """
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding
