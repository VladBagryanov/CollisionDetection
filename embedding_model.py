# from typing import List, Optional
# import numpy as np
# import hashlib
# import json
# from pathlib import Path
# import torch
# from sentence_transformers import SentenceTransformer
# from fact_consistency_rag import EmbeddingModelBase

# class CachedSentenceTransformer(EmbeddingModelBase):
#     def __init__(
#         self,
#         model_name: str = "all-MiniLM-L6-v2",
#         cache_dir: str = "./cache",
#         device: Optional[str] = None
#     ):
#         """Initialize the cached sentence transformer.
        
#         Args:
#             model_name: Name of the sentence-transformers model to use
#             cache_dir: Directory to store embedding cache
#             device: Device to run the model on (cuda/cpu)
#         """
#         self.model_name = model_name
#         self.cache_dir = Path(cache_dir)
#         self.cache_dir.mkdir(parents=True, exist_ok=True)
        
#         # Set device
#         if device is None:
#             device = "cuda" if torch.cuda.is_available() else "cpu"
        
#         # Initialize model
#         self.model = SentenceTransformer(model_name, device=device)
        
#         # Create cache subdirectory for this model
#         self.model_cache_dir = self.cache_dir / self.model_name
#         self.model_cache_dir.mkdir(exist_ok=True)

#     def encode(self, texts: List[str]) -> np.ndarray:
#         """Encode texts to embeddings with caching.
        
#         Args:
#             texts: List of texts to encode
        
#         Returns:
#             numpy array of embeddings
#         """
#         # Initialize results array
#         all_embeddings = []
#         texts_to_encode = []
#         cache_keys = []
        
#         # Check cache for each text
#         for text in texts:
#             cache_key = self._get_cache_key(text)
#             cache_file = self.model_cache_dir / f"{cache_key}.npy"
            
#             if cache_file.exists():
#                 # Load from cache
#                 embedding = np.load(cache_file)
#                 all_embeddings.append(embedding)
#             else:
#                 # Mark for encoding
#                 texts_to_encode.append(text)
#                 cache_keys.append(cache_key)
        
#         # Encode new texts if any
#         if texts_to_encode:
#             new_embeddings = self.model.encode(
#                 texts_to_encode,
#                 convert_to_numpy=True,
#                 show_progress_bar=False
#             )
            
#             # Cache new embeddings
#             for idx, (embedding, cache_key) in enumerate(zip(new_embeddings, cache_keys)):
#                 cache_file = self.model_cache_dir / f"{cache_key}.npy"
#                 np.save(cache_file, embedding)
#                 all_embeddings.append(embedding)
        
#         return np.vstack(all_embeddings)

#     def _get_cache_key(self, text: str) -> str:
#         """Generate a cache key for a text.
        
#         Args:
#             text: Input text
        
#         Returns:
#             Cache key string
#         """
#         # Create deterministic hash of text
#         text_bytes = text.encode('utf-8')
#         return hashlib.sha256(text_bytes).hexdigest()

#     def clear_cache(self) -> None:
#         """Clear the embedding cache."""
#         if self.model_cache_dir.exists():
#             for cache_file in self.model_cache_dir.glob("*.npy"):
#                 cache_file.unlink() 