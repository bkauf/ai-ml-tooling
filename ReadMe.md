## Load Data with Model Streamer in vLLM on Google Cloud


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
install vLLM with Run AI loader
```sh
pip3 install vllm[runai]
```

# Running vLLM with a model from GCS
Requires running from root

```sh
sudo su
source venv/bin/activate
```

Set vars
```sh
RUNAI_STREAMER_S3_USE_VIRTUAL_ADDRESSING=0
RUNAI_STREAMER_S3_ENDPOINT=https://storage.googleapis.com AWS_ENDPOINT_URL=https://storage.googleapis.com
RUNAI_STREAMER_S3_TRACE=1
AWS_EC2_METADATA_DISABLED=true
```
You currently need to get the account keys and secrets for GCS object storage to put in the AWS keys below. You can get them in the cloud console->storage ->settings create keys

Start vLLM
```sh
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY RUNAI_STREAMER_S3_ENDPOINT=https://storage.googleapis.com AWS_ENDPOINT_URL=https://storage.googleapis.com vllm serve s3://bkauf-models-usc/Llama-3.1-70B-Instruct --load-format runai_streamer --swap-space 10
```


# Hyperdisk ML Disk Attach

```sh
export ZONE=""
export DISK_NAME=""
export VM_NAME=""
```

```sh
gcloud compute instances attach-disk $VM_NAME --disk=$DISK_NAME --zone=$ZONE --mode=ro
```

Mount the disk assuming lsblk output shows it to be sdb
```sh
sudo mount -o ro,noload /dev/sdb /mnt/disks
```




