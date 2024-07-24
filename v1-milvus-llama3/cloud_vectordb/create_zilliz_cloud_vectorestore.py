import uuid
from llama_index.core import Document
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
    
zo = ZillizOps()

# Create Documents
class VectorStore:
    def __init__(self):
        self.documents = []
        self.image_documents = []
        self.retrieve_contents = []
        self.retriever = None

    def create_documents(self, elements, summaries, doc_type):
        for e, s in zip(elements, summaries):
            i = str(uuid.uuid4())
            doc = Document(
                metadata={'id': i, 'type': doc_type, 'original_content': e, 'summary': s}
            )
            self.retrieve_contents.append((i, e))
            self.documents.append(doc)

    def create_docs_caller(self, text_elements, text_summaries, 
                           table_elements, table_summaries):
        self.create_documents(text_elements, text_summaries, 'text')
        self.create_documents(table_elements, table_summaries, 'table')

    def upsert_docs_to_zilliz_coll(self):
        # store in json 
        batch_size = 2
        for i in range(0, len(self.documents), batch_size):
            last = min(i+batch_size, len(self.documents))
            batch = self.documents[i:last]
            id_b, orig_b, type_b, summ_b = [], [], [], []
            for doc in batch:
                # print(type(doc))
                id_b.append(str(doc.metadata['id'])[:100])
                orig_b.append(str(doc.metadata['original_content'])[:2500])
                type_b.append(str(doc.metadata['type'])[:7])
                summ_b.append(str(doc.metadata['summary'])[:2500])
            #
            status = zo.insert_docs(id_b, orig_b, type_b, summ_b)
            # status = zo.insert_image_docs(id_b, orig_b, type_b, summ_b)
            print(status)

    ## process image docs
    def create_image_documents(self, elements, summaries, doc_type):
        for e, s in zip(elements, summaries):
            i = str(uuid.uuid4())
            doc = Document(metadata={'id': i, 'type': doc_type, 'original_content': e, 'summary': s})
            self.retrieve_contents.append((i, e))
            self.image_documents.append(doc)

    def create_image_docs_caller(self, image_elements, image_summaries):
        self.create_image_documents(image_elements, image_summaries, 'image')

    def upsert_image_docs_to_zilliz_coll(self):
        batch_size = 2
        for i in range(0, len(self.image_documents), batch_size):
            last = min(i+batch_size, len(self.image_documents))
            batch = self.image_documents[i:last]
            id_b, orig_b, type_b, summ_b = [], [], [], []
            for doc in batch:
                # print(type(doc))
                id_b.append(str(doc.metadata['id'])[:100])
                orig_b.append(str(doc.metadata['original_content'])[:2500])
                type_b.append(str(doc.metadata['type'])[:7])
                summ_b.append(str(doc.metadata['summary'])[:2500])
            #
            status = zo.insert_image_docs(id_b, orig_b, type_b, summ_b)
            print(status)

# text_elements = ...
# text_summaries = ...
# table_elements = ...
# table_summaries = ...
# image_elements = ...
# image_summaries = ...

# vs_obj = VectorStore()
# vs_obj.create_docs_caller(text_elements, text_summaries, table_elements, table_summaries)
# vs_obj.upsert_docs_to_zilliz_coll()

# vs_obj.create_image_docs_caller(image_elements, image_summaries)
# vs_obj.upsert_image_docs_to_zilliz_coll()