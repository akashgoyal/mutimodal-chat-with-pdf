Internal Flow :
1. extract_data_from_pdf.py
2. llms_init.py
3. generate_summaries.py
4. create_vectorstore_index.py OR create_zilliz_cloud_vectorstore.py

How to test :
python main_local.py

Use streamlit app :
streamlit run sl_app.py


Two versions :
1. Local - suitable for small pdfs. UI support. Milvus Index exists locally. Images are resized to smaller dimension.
2. Other - Makes use of Zilliz clusters & collection. Large pdfs data is embedded & stored as part of preprocessing. Images are of original size.
