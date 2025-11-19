from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# df = pd.read_csv('restaurants_osm.csv')
df = pd.read_csv('restaurant.csv')
embeddings = OllamaEmbeddings(model='mxbai-embed-large')

db_location = './chrom_langchain_db'
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content = str(row['name']) + ' ' + str(row['restaurant_type']),
            metadata = {'name':row['name'],'price': row['price'], 'address': row['address'], 
                        'comment': row['comment'], 'restaurant_type': row['restaurant_type']},
            id = str(i)
        )
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name = 'restaurant_reviews',
    persist_directory = db_location,
    embedding_function = embeddings,
)

if add_documents:
    vector_store.add_documents(documents = documents, ids = ids)

def build_retriever():
    retriever = vector_store.as_retriever(
        search_kwargs = {'k': 5}
    )
    return retriever

# def build_vector_store():
#     """
#     回傳底層 Chroma vector_store 以便呼叫 similarity_search_with_score。
#     """
#     return vector_store

if __name__ == "__main__":
    retriever = vector_store.as_retriever(
        search_kwargs = {'k': 5}
    )
    query = "請推薦一家價格便宜的義大利餐廳"
    results = retriever.get_relevant_documents(query)
    for doc in results:
        print(doc.page_content, doc.metadata)