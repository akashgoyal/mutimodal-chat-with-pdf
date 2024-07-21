import base64
from IPython.display import display, Image

import extract_data_from_pdf as ed
import generate_summaries as gs
import create_vectorstore_index as cv

## step 1
output_path = './content/images'
filename = "./content/test-pdf.pdf"
# filename = "./content/top10touristplaceinindiainsummer.pdf"
# filename = "./content/touristplace-image-pdf.pdf"

retriever = None
def process_pdf(filename, output_path):
    pdex_obj = ed.PDFExtractor(filename, output_path, bool_resize=True)
    pdex_obj.partition_pdf()
    pdex_obj.extract_elements()

    # step 2
    text_summaries = []
    text_summaries = gs.process_text_elements(pdex_obj.text_elements)
    table_summaries = []
    table_summaries = gs.process_table_elements(pdex_obj.table_elements)
    image_summaries = []
    image_summaries = gs.process_image_elements(pdex_obj.image_elements)

    # step 3
    vs_obj = cv.VectorStore()
    vs_obj.create_docs_caller(
        pdex_obj.text_elements, text_summaries, 
        pdex_obj.table_elements, table_summaries, 
        pdex_obj.image_elements, image_summaries)
    vs_obj.create_milvus_vs()
    
    retriever = vs_obj.retriever

# step 4
prompt_template = """
    You are an assistant tasked with summarizing tables and text.
    Give a concise summary of the table or text.
    Answer the question based only on the following context, which can include text, images, and tables:
    {context}
    Question: {question}
    Don't answer if you are not sure and decline to answer and say "Sorry, I don't have much information about it."
    Just return the helpful answer in as much detail as possible.
    Answer:
"""

from llms_init import my_llm
def chat_with_llm(question):
    nodes = retriever.retrieve(question)
    relevant_docs = [n.node for n in nodes]

    context = ""
    relevant_images = []
    for d in relevant_docs:
        if d.metadata['type'] == 'text':
            context += '[text]' + d.metadata['original_content']
        elif d.metadata['type'] == 'table':
            context += '[table]' + d.metadata['original_content']
        elif d.metadata['type'] == 'image':
            # print(d.metadata.keys())
            context += '[image]' + str(d.page_content)
            relevant_images.append(d.metadata['original_content'])
    # result = qa_chain.run({'context': context, 'question': question})
    result = my_llm.complete(prompt_template.format(context=context, question=question))
    return result, relevant_images


# # step 5
# while True:
#     question = input("Enter your question: ")
#     if question == "quit":
#         break
#     result, relevant_images = answer(question)
#     print(result)
#     print(relevant_images)
#     image_data = base64.b64decode(relevant_images[0])
#     display(Image(image_data))
    