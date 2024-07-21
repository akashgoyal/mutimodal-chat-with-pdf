from pymilvus import MilvusClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from dotenv import load_dotenv
load_dotenv('.env')

jina_embedding_model = HuggingFaceEmbedding(model_name="jinaai/jina-embeddings-v2-base-en") # 768

coll_name = "economic_survey_202223"

client = MilvusClient(
    uri="https://in03-312179d826c78ab.api.gcp-us-west1.zillizcloud.com", 
    token="eb9b1edeb3cfa3d3bd983fe9544bbe2e58a65019a0589e76d1e63361a73d1a6158793db627213d0d8141e623f5cca8889c013287")

client.describe_collection(collection_name=coll_name)


# Upsert data
# [id, vector, original_content, type, summary]
def insert_docs(id=[], orig=[], type=[], summ=[]):
    cnt = len(id)
    vectors = jina_embedding_model._embed(orig)
    print("Vectors shape:", len(vectors))
    print("Vectors:", len(vectors[0]))
    data = [
        {"id":id[i], "vector":vectors[i], "original_content":orig[i], "type": type[i], "summary": summ[i]}
        for i in range(cnt) 
    ]
    status = client.insert(collection_name=coll_name, data=data)
    return status

# Sample inputs
# ids = [1, 2, 3]
# original_contents = ["Lorem ipsum", "dolor sit amet", "consectetur adipiscing elit"]
# types = ["A", "B", "C"]
# summaries = ["Lorem", "ipsum", "dolor"]

# # Call the insert_docs function with the sample inputs
# insert_docs(id=ids, orig=original_contents, type=types, summ=summaries)


def search_collection(input_queries=["Who is Alan Turing?"]):
    query_vectors = jina_embedding_model._embed(input_queries)
    res = client.search(
        collection_name=coll_name,  # target collection
        data=query_vectors,  # query vectors
        limit=3,  # number of returned entities
        output_fields=["summary", "original_content", "type"],  # specifies fields to be returned
    )
    return res
# Prepare input to test search_collection method
# queries = ["What is lorem ipsum?", "How does sit amet related?"]
# results = search_collection(input_queries=queries)
# print("##########")
# # print(results)
# for node_list in results:
#     print(type(node_list))
#     for nd in node_list:
#         node = nd["entity"]
#         print(node["type"], node["summary"], node["original_content"])

