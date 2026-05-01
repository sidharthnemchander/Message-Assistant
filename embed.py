from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text):
    vector = embed_model.encode(text)
    return vector.tolist()