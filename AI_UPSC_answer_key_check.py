import os, io

from google.cloud import vision
from google.cloud.vision_v1 import types
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'AI_UPSC_answer_key.json'


client = vision.ImageAnnotatorClient()


file_name = 'test1.png'
image_path = f'C:/Users/Pratik/Desktop/UPSCANSWER/{file_name}'

with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

# construct an image instance
image = types.Image(content=content)

"""
# or we can pass the image url
image = types.Image()
image.source.image_uri = 'https://edu.pngfacts.com/uploads/1/1/3/2/11320972/grade-10-english_orig.png'
"""

# annotate Image Response
response = client.text_detection(image=image)

plain_text = response.full_text_annotation.text


print(plain_text)
