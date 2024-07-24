from typing import Any
from unstructured.partition.pdf import partition_pdf
import base64
import cv2
import os
import shutil


class PDFExtractor:
    def __init__(self, filename, output_path, max_resized_width=250, bool_resize=False):
        self.filename = filename
        self.output_path = output_path
        self.bool_resize = bool_resize # true if local run
        self.max_width = max_resized_width # use only if bool_resize is true
        self.raw_pdf_elements = []
        self.text_elements = []
        self.table_elements = []
        self.image_elements = []

    def partition_pdf(self):
        if os.path.exists("./figures"):
            shutil.rmtree("./figures")
        os.makedirs("./figures")
        
        self.raw_pdf_elements = partition_pdf(
            filename=self.filename,
            strategy='auto',
            extract_images_in_pdf=True,
            extract_image_block_types=["Image", "Table"],
            infer_table_structure=True,
            chunking_strategy="by_title",
            max_characters=2500,
            new_after_n_chars=2400,
            combine_text_under_n_chars=1000,
            image_output_dir_path=self.output_path,
        )

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def resize_image(self, image_path):
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        ratio = self.max_width / float(width)
        new_height = int(height * ratio)
        resized = cv2.resize(img, (self.max_width, new_height), interpolation=cv2.INTER_AREA)
        cv2.imwrite(image_path, resized)
        print(f"Resized {image_path} to {self.max_width}x{new_height}")
        return image_path

    def extract_elements(self):
        for element in self.raw_pdf_elements:
            if 'CompositeElement' in str(type(element)):
                self.text_elements.append(element)
            elif 'Table' in str(type(element)):
                self.table_elements.append(element)

        self.table_elements = [i.text for i in self.table_elements]
        self.text_elements = [i.text for i in self.text_elements]

        for image_file in os.listdir("./figures"):
            if image_file.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join("./figures", image_file)
                if self.bool_resize:
                    self.resize_image(image_path) 
                encoded_image = self.encode_image(image_path)
                self.image_elements.append(encoded_image)


# output_path = './content/images'
# filename = "./content/Economic-Survey-Complete-PDF.pdf"
# filename = "./content/echap04.pdf"

# pdf_extractor = PDFExtractor(filename, output_path, 100, True)
# pdf_extractor.partition_pdf()
# pdf_extractor.extract_elements()
# self.text_elements = []
# self.table_elements = []
# self.image_elements = []