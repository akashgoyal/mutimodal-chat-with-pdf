from llama_index.llms.together import TogetherLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv('.env')

my_llm = TogetherLLM(model="meta-llama/Llama-3-70b-chat-hf", api_key=os.getenv("TOGETHER_API_KEY"))
jina_embedding_model = HuggingFaceEmbedding(model_name="jinaai/jina-embeddings-v2-base-en") # 768

from llama_index.core import Settings
Settings.llm = my_llm
Settings.embed_model = jina_embedding_model
Settings.chunk_size = 32000

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY1"))
