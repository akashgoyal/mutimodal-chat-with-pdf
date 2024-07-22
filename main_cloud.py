import base64
from IPython.display import display, Image

import extract_data_from_pdf as ed
import generate_summaries as gs
import cloud_vectordb.create_zilliz_cloud_vectorestore as cv

## step 1
output_path = './content/images'
filename = "./content/test-pdf.pdf"
filename = "./content/top10touristplaceinindiainsummer.pdf"
# filename = "./content/touristplace-image-pdf.pdf"

retriever = None
def process_pdf(filename, output_path = './content/images'):
    pdex_obj = ed.PDFExtractor(filename, output_path, max_resized_width=250, bool_resize=True)
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
        pdex_obj.table_elements, table_summaries)
    vs_obj.upsert_docs_to_zilliz_coll()

    vs_obj.create_image_docs_caller(
        pdex_obj.image_elements, image_summaries)
    vs_obj.upsert_image_docs_to_zilliz_coll()

    global retriever
    retriever = vs_obj.retriever

# process_pdf(filename, output_path = './content/images')

# step 4
def cloud_retriever(queries=['what is title of the document?']):
    results = cv.zo.search_collection(input_queries=queries)
    res = []
    for node_list in results:
        print(type(node_list))
        for nd in node_list:
            node = nd["entity"]
            # print(node["type"], node["summary"], node["original_content"])
            res.append(node)
    return res

# step 5
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

def cloud_chat_with_llm(question):
    relevant_docs = cloud_retriever([question])

    context = ""
    relevant_images = []
    for node in relevant_docs:
        type, summary, orig_content = node["type"], node["summary"], node["original_content"]
        if type == 'text':
            context += '[text]' + orig_content
        elif type == 'table':
            context += '[table]' + orig_content
        elif type == 'image':
            # print(d.metadata.keys())
            context += '[image]' + summary
            relevant_images.append(orig_content)
    # result = qa_chain.run({'context': context, 'question': question})
    result = my_llm.complete(prompt_template.format(context=context, question=question))
    return result, relevant_images


# while True:
#     question = input("Enter your question: ")
#     if question == "quit":
#         break
#     result, relevant_images = cloud_chat_with_llm(question)
#     print(result)
#     print(relevant_images)
#     image_data = base64.b64decode(relevant_images[0])
#     display(Image(image_data))
    