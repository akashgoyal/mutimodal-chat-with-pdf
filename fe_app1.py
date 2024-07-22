import streamlit as st
import base64
from PIL import Image
import io
import os

# Import your backend functions
from main_local import process_pdf, chat_with_llm

def main():
    st.title("PDF Chat with LLM")

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Process the PDF
        if st.button("Process PDF"):
            with st.spinner("Processing PDF and creating vectorstore..."):
                try:
                    process_pdf("temp.pdf", output_path='./content/images')
                    st.success("PDF processed and vectorstore created!")
                except Exception as e:
                    st.error(f"An error occurred while processing the PDF: {str(e)}")
                finally:
                    # Clean up the temporary file
                    if os.path.exists("temp.pdf"):
                        os.remove("temp.pdf")

        # Chat interface
        st.subheader("Chat with your PDF")
        user_input = st.text_input("Ask a question about your PDF:")
        
        if user_input:
            try:
                with st.spinner("Generating response..."):
                    result, relevant_images = chat_with_llm(user_input)
                    
                    # Display text result
                    st.write("Response:", result)
                    
                    # Display images if any
                    if relevant_images:
                        st.subheader("Related Images:")
                        for idx, img_base64 in enumerate(relevant_images):
                            try:
                                img_data = base64.b64decode(img_base64)
                                img = Image.open(io.BytesIO(img_data))
                                st.image(img, caption=f"Image {idx+1}", use_column_width=True)
                            except Exception as img_error:
                                st.warning(f"Couldn't display image {idx+1}: {str(img_error)}")
            except Exception as chat_error:
                st.error(f"An error occurred while processing your question: {str(chat_error)}")

    else:
        st.info("Please upload a PDF file to begin.")

if __name__ == "__main__":
    main()