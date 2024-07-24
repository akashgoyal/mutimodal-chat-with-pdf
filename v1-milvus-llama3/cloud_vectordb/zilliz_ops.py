from pymilvus import MilvusClient
import llms_init
import os
from dotenv import load_dotenv
load_dotenv('.env')

class ZillizOps:
    def __init__(self):
        self.embedding_model = llms_init.my_embed_model
        self.coll_name = "economic_survey_202223"
        self.client = MilvusClient(uri=os.getenv("ZILLIZ_URI"), token=os.getenv("ZILLIZ_TOKEN"))

    def insert_docs(self, id=[], orig=[], type=[], summ=[]):
        cnt = len(id)
        vectors = self.embedding_model._embed(orig)
        # print("Vectors shape:", len(vectors))
        # print("Vectors:", len(vectors[0]))
        data = [
            {"id":id[i], "vector":vectors[i], "original_content":orig[i], "type": type[i], "summary": summ[i]}
            for i in range(cnt) 
        ]
        status = self.client.insert(collection_name=self.coll_name, data=data)
        return status

    def insert_image_docs(self, id=[], orig=[], type=[], summ=[]):
        cnt = len(id)
        vectors = self.embedding_model._embed(summ)
        print("Vectors shape:", len(vectors))
        print("Vectors:", len(vectors[0]))
        data = [
            {"id":id[i], "vector":vectors[i], "original_content":orig[i], "type": type[i], "summary": summ[i]}
            for i in range(cnt) 
        ]
        status = self.client.insert(collection_name=self.coll_name, data=data)
        return status

    def search_collection(self, input_queries=["Who is Alan Turing?"]):
        query_vectors = self.embedding_model._embed(input_queries)
        res = self.client.search(
            collection_name=self.coll_name,  # target collection
            data=query_vectors,  # query vectors
            limit=3,  # number of returned entities
            output_fields=["summary", "original_content", "type"],  # specifies fields to be returned
        )
        return res

# Sample usage
zilliz_ops = ZillizOps()
zilliz_ops.insert_docs(id=["1", "2", "3"], orig=["Lorem ipsum", "dolor sit amet", "consectetur adipiscing elit"], type=["A", "B", "C"], summ=["Lorem", "ipsum", "dolor"])
results = zilliz_ops.search_collection(input_queries=["What is lorem ipsum?", "How does sit amet related?"])
for node_list in results:
    for nd in node_list:
        node = nd["entity"]
        print(node["type"], node["summary"], node["original_content"])
