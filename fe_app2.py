import streamlit as st
import time
import base64
from io import BytesIO
from PIL import Image
import os
import tempfile

# Assuming you have these functions implemented
from main_local import process_pdf, chat_with_llm
from main_cloud import cloud_chat_with_llm

def main():
    st.title("LLM Chat Application")

    # Use custom CSS to add padding and improve layout
    st.markdown("""
        <style>
        .stColumn > div > div > div > div {
            padding: 0 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create two columns for the layout with more space between them
    col1, spacer, col2 = st.columns([10, 1, 10])

    with col1:
        st.header("PDF-based Local Chat")
        pdf_based_chat()

    with col2:
        st.header("Direct Chat")
        direct_chat()

def pdf_based_chat():
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Process the PDF
        if st.button("Process PDF"):
            with st.spinner("Processing PDF and creating vectorstore..."):
                # Save the uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                try:
                    # Simulate processing time
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.05)  # Simulate work being done
                        progress_bar.progress(i + 1)
                    
                    # Actually process the PDF
                    process_pdf(tmp_file_path)
                    
                    st.success("PDF processed and vectorstore created!")
                finally:
                    # Clean up the temporary file
                    os.unlink(tmp_file_path)

        # Chat interface
        st.subheader("Chat about your PDF")
        user_input = st.text_input("Ask a question about your PDF:", key="pdf_input")
        
        if user_input:
            with st.spinner("Generating response..."):
                # Get response from LLM
                result, images = chat_with_llm(user_input)
                
                # Display text result
                st.write("Response:", result)
                
                # Display images if any
                display_images(images)
    else:
        st.info("Please upload a PDF file to begin.")

def direct_chat():
    st.subheader("Zilliz Cloud VectorDB - Direct Chat LLM")
    user_input = st.text_input("Ask a question:", key="direct_input")

    if user_input:
        with st.spinner("Generating response..."):
            # Get response from cloud-based LLM
            result, images = cloud_chat_with_llm(user_input)
            
            # Display text result
            st.write("Response:", result)
            
            # Display images if any
            display_images(images)

def display_images(images):
    if images:
        st.subheader("Related Images:")
        for idx, img_base64 in enumerate(images):
            try:
                img_data = base64.b64decode(img_base64)
                img = Image.open(BytesIO(img_data))
                st.image(img, caption=f"Image {idx+1}", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image {idx+1}: {str(e)}")

if __name__ == "__main__":
    main()