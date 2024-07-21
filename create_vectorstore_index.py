import uuid
from llama_index.core import Document
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex


# Create Documents
class VectorStore:
    def __init__(self):
        self.documents = []
        self.retrieve_contents = []
        self.retriever = None

    def create_documents(self, elements, summaries, doc_type):
        for e, s in zip(elements, summaries):
            i = str(uuid.uuid4())
            doc = Document(
                page_content=s,
                metadata={'id': i, 'type': doc_type, 'original_content': e}
            )
            self.retrieve_contents.append((i, e))
            self.documents.append(doc)

    def create_docs_caller(self, text_elements, text_summaries, 
                           table_elements, table_summaries, 
                           image_elements, image_summaries):
        self.create_documents(text_elements, text_summaries, 'text')
        self.create_documents(table_elements, table_summaries, 'table')
        self.create_documents(image_elements, image_summaries, 'image')

    def create_milvus_vs(self):
        vector_store_jina = MilvusVectorStore(
            uri="./milvus_llama.db", 
            collection_name="my_multimodal_data", dim=768, overwrite=True
            )
        storage_context_jina = StorageContext.from_defaults(vector_store=vector_store_jina)
        vector_index_jina = VectorStoreIndex.from_documents(self.documents, storage_context=storage_context_jina)

        self.retriever = vector_index_jina.as_retriever(similarity_top_k=3)


# text_elements = ...
# text_summaries = ...
# table_elements = ...
# table_summaries = ...
# image_elements = ...
# image_summaries = ...

# vs_obj = VectorStore()
# vs_obj.create_docs_caller(text_elements, text_summaries, table_elements, table_summaries, image_elements, image_summaries)
# vs_obj.create_milvus_vs()