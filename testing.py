import json
import re
import os
from google.cloud import vision
from google.cloud import storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'AI_UPSC_answer_key.json'

def async_detect_document(gcs_source_uri, gcs_destination_uri):
    """OCR with PDF/TIFF as source files on GCS"""
    mime_type = 'application/pdf'
    batch_size = 2

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

    storage_client = storage.Client()

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    blob_list = [blob for blob in list(bucket.list_blobs(
        prefix=prefix)) if not blob.name.endswith('/')]
    print('Output files:')
    for blob in blob_list:
        print(blob.name)

    output = blob_list[0]
    json_string = output.download_as_text()
    response = json.loads(json_string)

    first_page_response = response['responses'][0]
    annotation = first_page_response['fullTextAnnotation']

    output_text = annotation['text']

    # Save the output as plain text
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(output_text)


gcs_source_uri = 'gs://uploads_upsc/Upsctest.pdf'
gcs_destination_uri = 'gs://uploads_upsc/pdf_result'

async_detect_document(gcs_source_uri, gcs_destination_uri)
