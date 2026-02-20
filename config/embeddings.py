from chromadb.api.types import EmbeddingFunction
from sentence_transformers import SentenceTransformer
import torch

_model = None


class BGEEmbeddingFunction(EmbeddingFunction):

    def __init__(self):
        global _model

        if _model is None:
            _model = SentenceTransformer(
                "BAAI/bge-large-en-v1.5",
                device="cuda" if torch.cuda.is_available() else "cpu"
            )

        self.model = _model

    def __call__(self, input):
        embeddings = self.model.encode(
            input,
            normalize_embeddings=True
        )
        return embeddings.tolist()


_embedding_instance = None


def get_embedding_function():
    global _embedding_instance

    if _embedding_instance is None:
        _embedding_instance = BGEEmbeddingFunction()

    return _embedding_instance