


import os, io
import re
from google.cloud import vision
from google.cloud import storage
from google.protobuf import json_format
from google.cloud.vision_v1 import types


""" 
# pip install --upgrade google-cloud-storage
"""
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'AI_UPSC_answer_key.json'
client = vision.ImageAnnotatorClient()

batch_size = 2
mime_type = 'application/pdf'
feature = types.Feature(
    type=types.Feature.Type.DOCUMENT_TEXT_DETECTION
    )

gcs_source_uri = 'gs://uploads_upsc/Day39.pdf'
gcs_source = types.GcsSource(uri=gcs_source_uri)
input_config = types.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

gcs_destination_uri = 'gs://uploads_upsc/pdf_result'
gcs_destination = types.GcsDestination(uri=gcs_destination_uri)
output_config = types.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

async_request = types.AsyncAnnotateFileRequest(
    features=[feature], input_config=input_config, output_config=output_config)

operation = client.async_batch_annotate_files(requests=[async_request])
operation.result(timeout=180)

storage_client = storage.Client()
match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
bucket_name = match.group(1)
prefix = match.group(2)
bucket = storage_client.get_bucket(bucket_name)

# List object with the given prefix
blob_list = list(bucket.list_blobs(prefix=prefix))
print('Output files:')
for blob in blob_list:
    print(blob.name)

output = blob_list[0]
json_string = output.download_as_string()
response = json_format.Parse(
            json_string, types.AnnotateFileResponse())

first_page_response = response.responses[0]
annotation = first_page_response.full_text_annotation

print(u'Full text:')
print(annotation.text)