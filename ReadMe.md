## Load Data with Model Streamer in vLLM on Google Cloud


# Transfer Data from Hugging Face to GCS

Use data-loading/hf-gcs.py script. Change vars to match model/folder names 

#Prep VM Machine for vLLM teseting

## install CUDA and drivers
https://cloud.google.com/compute/docs/gpus/install-drivers-gpu

## Create a virtual envoinment and install dependencies 
 ```sh
sudo  apt install python3.11-venv
sudo apt install python3-pip
mkdir vllm
cd vllm
python3 -m venv venv
```

### Activate the Envonrionment
 ```sh
 source venv/bin/activate
```
### Install vLLM with [Run AI loader](https://docs.vllm.ai/en/latest/models/extensions/runai_model_streamer.html)
```sh
pip3 install vllm[runai]
```

# Running vLLM with a model from GCS
## Note - Make sure you don't have sub folders in your GCS bucket that have "original" copies of the OSS models


```sh
vllm serve gs://bkauf-models-usc/DeepSeek-R1-Distill-Llama-8B --load-format=runai_streamer --served-model-name deepSeek8B
```

# GIQ & K8s Manifests 



gcloud container ai profiles manifests create --model=meta-llama/Llama-3.3-70B-Instruct \
--model-server=vllm --model-server-version=v0.7.2 --accelerator-type=nvidia-h100-80gb    



## Setup workload Identity 


## Create IAM Rules for workload identity bucket access

```sh
export BUCKET=""
export PROJECT_NUMBER=""
export PROJECT_ID=""
export SERVICE_ACCOUNT="gcs-access"



gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$PROJECT_ID.svc.id.goog/subject/ns/default/sa/$SERVICE_ACCOUNT --role roles/storage.bucketViewer

gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$PROJECT_ID.svc.id.goog/subject/ns/default/sa/$SERVICE_ACCOUNT --role roles/storage.objectUser

```


#Enable [Anywhere Cache](https://cloud.google.com/storage/docs/anywhere-cache) for Zonal Caching
```sh
export ZONE="us-central1-c"

gcloud storage buckets anywhere-caches create gs://$BUCKET $ZONE
```
##Check the status of the cache
```sh
gcloud storage buckets anywhere-caches describe $BUCKET/$ZONE
```
