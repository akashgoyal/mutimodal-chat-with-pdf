from llms_init import my_llm, openai_client


def summarize_text(text_element):
    prompt = f"Summarize the following text:\n\n{text_element}\n\nSummary:"
    response = my_llm.complete(prompt)
    return response

# Function for table summaries
def summarize_table(table_element):
    prompt = f"Summarize the following table:\n\n{table_element}\n\nSummary:"
    response = my_llm.complete(prompt)
    return response

#
client = openai_client
MODEL="gpt-4o-mini"

def summarize_image(base64_image):
  response = client.chat.completions.create(
      model=MODEL,
      messages=[
          {"role": "system", "content": "You are a helpful assistant who analyzes images."},
          {"role": "user", "content": [
              {"type": "text", "text": "Describe the contents of this image precisely in under 100 words."},
              {"type": "image_url", "image_url": {
                  "url": f"data:image/png;base64,{base64_image}"}
              }
          ]}
      ],
      temperature=0.0,
  )
  summ = response.choices[0].message.content
  print(summ)
  return summ


####################
def process_text_elements(text_elements):
    text_summaries = []
    for i, te in enumerate(text_elements):
        summary = summarize_text(te)
        text_summaries.append(summary)
        #print(f"{i + 1}th element of texts processed.")
    return text_summaries

def process_table_elements(table_elements):
    table_summaries = []
    for i, te in enumerate(table_elements):
        summary = summarize_table(te)
        table_summaries.append(summary)
        #print(f"{i + 1}th element of tables processed.")
    return table_summaries

##############
import base64
def get_image_size(image_element):
    image_data = base64.b64decode(image_element)
    size_in_bytes = len(image_data)
    size_in_mb = size_in_bytes / (1024 * 1024)
    return size_in_mb


def process_image_elements(image_elements):
    image_summaries = []
    for i, ie in enumerate(image_elements):
        if get_image_size(ie) > 20:
            continue
        summary = summarize_image(ie)
        image_summaries.append(summary)
    return image_summaries

