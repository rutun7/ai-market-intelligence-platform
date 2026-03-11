import faiss
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Load knowledge
with open("rag_data.txt","r",encoding="utf8") as f:
    documents = f.read().split("\n")


# Create embeddings
embeddings = []

for doc in documents:

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc
    )

    embeddings.append(response.data[0].embedding)


dimension = len(embeddings[0])

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings).astype("float32"))


def retrieve_context(query, k=3):

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    query_embedding = np.array([response.data[0].embedding]).astype("float32")

    distances, indices = index.search(query_embedding, k)

    results = []

    for i in indices[0]:
        results.append(documents[i])

    return results
