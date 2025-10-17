# Load Data into GPUs fast with Model Streamer in vLLM on Google Cloud

The [Run:ai model streamer](https://docs.vllm.ai/en/latest/models/extensions/runai_model_streamer.html) loads models from object storage to GPU memory direct from CPU memory. It is a package available for vLLM and greatly accelerates model download times.

## Prep VM Machine for vLLM testing

To test the model streamer on a GCE instance, create one that has a single Nvidia L4 GPU. Then [install CUDA and drivers](https://cloud.google.com/compute/docs/gpus/install-drivers-gpu).

1. Create a virtual envoinment and install dependencies 

```sh 
sudo apt install python3.11-venv
sudo apt install python3-pip
mkdir vllm
cd vllm
python3 -m venv venv
```

2. Activate the Environment

```sh
source venv/bin/activate
```

3. Transfer Data from Hugging Face to GCS

 Use data-loading/hf-gcs.py script from any machine you can login to hugging face from. Change vars to match model/folder names 
```sh
repo_id="google/gemma-3-4b-it" 
local_dir="/tmp"
gcs_bucket_name="" 
gcs_prefix="gemma-3-4b-it"
```

4. Install the dependencides needed

```sh
pip3 install google-cloud-storage
pip3 install huggingface_hub
```

5. Login to Huggingface

Get a token from Hugging face and use it to login via CLI
```sh
hf auth login
```

6. Login to Google Cloud via CLI if not already logged in
```sh
gcloud init
```

7. Run the script to populate the GCS bucket with the model from Huggingface
```sh
python3 data-loading/hf-gcs.py
```

7. Install vLLM with [Run AI loader](https://docs.vllm.ai/en/latest/models/extensions/runai_model_streamer.html)
```sh
pip3 install vllm[runai]
```

## Running vLLM with a model streaming from GCS

To use the model streamer you just need to add the "--load-format=runai_streamer" flag. Make sure you don't have sub folders in your GCS bucket that have "original" copies of the OSS models.

Example vllm command using a model in the following location *gs://models-usc/gemma-3-4b-it*

```sh
vllm serve gs://models-usc/gemma-3-4b-it --load-format=runai_streamer 
```

## GIQ & Kubernetes Manifests 

The following steps can help you use the model streamer on a GKE cluster

1. Setup workload Identity 

    If you are using an Autopilot GKE cluster workload identity is enabled by default. If using a GKE Standard cluster you will need to [enable it](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable_on_clusters_and_node_pools) if it not already on. 


2. Create IAM Rules for workload identity bucket access

    Create two policy bindings that the service account you will use in your GKE cluster can use to access the models in Google Cloud Object Storage

    ```sh
    export BUCKET=""
    export PROJECT_NUMBER=""
    export PROJECT_ID=""
    export SERVICE_ACCOUNT="gcs-access"

    gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$PROJECT_ID.svc.id.goog/subject/ns/default/sa/$SERVICE_ACCOUNT --role roles/storage.bucketViewer

    gcloud storage buckets add-iam-policy-binding gs://$BUCKET --member principal://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$PROJECT_ID.svc.id.goog/subject/ns/default/sa/$SERVICE_ACCOUNT --role roles/storage.objectUser
    ```
3. Sample deployment.yaml

    Use the sample **deployment.yaml** file and change model location and service account to use the Run:ai streamer on GKE with workload identity. If using autopilot you will need to modify the deployment.yaml file to include the [machine type needed in autopilot](https://cloud.google.com/kubernetes-engine/docs/how-to/autopilot-gpus#request-gpus)

    ```sh
    kubectl apply -f deployment.yaml
    ```
    View the logs to see the model streamer output
    ```sh 
    kubectl logs [pod name]
    ```


4. Optional- [Use Google Inference Quickstart](https://cloud.google.com/kubernetes-engine/docs/how-to/machine-learning/inference/inference-quickstart)

    The [Google Inference Quickstart](https://cloud.google.com/kubernetes-engine/docs/how-to/machine-learning/inference/inference-quickstart) can generate kubernetes manifests for you to use that have all autoscaling and metrics collection settings. These manefests are being updated to include the Run:ai model streamer. 

    Example Command for **gemma-3-4b-it** on **vllm** 

    ```sh
    gcloud container ai profiles manifests create --model=google/gemma-3-4b-it --model-server=vllm --accelerator-type=nvidia-l4 
    ```
    

## GCS [Anywhere Cache](https://cloud.google.com/storage/docs/anywhere-cache) for Zonal Caching

GCS anywhere cache can reduce load times by as much as 30% once a model is cached to a zone where the GPU is located. You can enable the cache with the following commands. This feature is very useful for scale out inference workloads.
     
```sh
    export ZONE="us-central1-c"

    gcloud storage buckets anywhere-caches create gs://$BUCKET $ZONE
        
     ## Check the status of the cache
     gcloud storage buckets anywhere-caches describe $BUCKET/$ZONE
```


### Creating Secrets in Kubernetes 

example 
```sh
kubectl create secret generic gcp-token --from-literal=gcp_api_token=xyz


kubectl create secret generic gcp-secret --from-literal=gcp_api_secret=xyz


```