"""
Google Cloud Util Functions:
- Upload to Google Storage Bucket
- Delete from Google Storage Bucket
- Generate signed URL
"""
import os
import datetime

from google.cloud import storage
from google.cloud.storage.blob import Blob

## Google Storage Client
client = storage.Client()

def upload_blob(bucket_name, source_file_name, destination_blob_name, content_type='', algo_unique_key=''):
    """Uploading File to Google Storage Bucket

    Args:
        bucket_name (str): Google Storage Bucket Name
        source_file_name (str): Local Absolute Filpath to upload
        destination_blob_name (str): File Name used to store in bucket
        content_type (str, optional): The content type of the file being uploaded
        algo_unique_key (str, optional): [description]. Defaults to ''. Algorithmia Data Source Bucket Unique Key

    Returns:
        [str]: Google Storage Object URI, if algorithmia key is given the same is modified.
    """
    
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name, content_type=content_type)

    data_uri = blob.self_link
    
    if algo_unique_key!="":
        return os.path.join("gs+{}://{}".format(algo_unique_key, bucket_name), data_uri.split("/")[-1])
    
    return os.path.join("gs://{}".format(bucket_name), data_uri.split("/")[-1])

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print("Blob {} deleted.".format(blob_name))

def download_video(bucket_name, filename, output_filename):
    bucket = client.get_bucket(bucket_name)
    # Create a blob object from the filepath
    blob = bucket.blob(filename)
    # Download the file to a destination
    blob.download_to_filename(output_filename)

    return output_filename

def generate_signed_url(output_uri):
    expiration_time = datetime.timedelta(minutes=5)

    blob = Blob.from_string(output_uri, client=client)
    
    signed_url = blob.generate_signed_url(expiration=expiration_time, version='v4', response_disposition='attachment')

    return signed_url            