import os
from huggingface_hub import snapshot_download
from google.cloud import storage

# change the below to match your Google Cloud and Huggingface model locations
repo_id="google/gemma-3-4b-it" 
local_dir="/tmp"
gcs_bucket_name="" 
gcs_prefix="gemma-3-4b-it"


def download_model_then_upload_model():
    # Ensure you're logged in to Hugging Face
    # You'll need to run `huggingface-cli login` first or set HF_TOKEN

    # Download model
    print(f"Downloading model {repo_id}...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,  # Important for full download
        resume_download=True,  # Resume interrupted downloads
        max_workers=10  # Parallel downloads
    )
    upload_model()



def upload_model():
    # Upload model to GCS
    # Initialize Google Cloud Storage client
    print(gcs_bucket_name)
    storage_client = storage.Client()
    bucket = storage_client.bucket(gcs_bucket_name)
    print(f"Uploading to GCS bucket {gcs_bucket_name}...")
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            blob_path = os.path.join(gcs_prefix, relative_path)
            
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            print(f"Uploaded: {local_path} to {blob_path}")

    print("Model download and upload complete!")


download_model_then_upload_model()