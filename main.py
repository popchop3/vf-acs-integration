import os
import yaml
import re
import pandas as pd
import numpy as np
import requests
from io import StringIO
from google.cloud import storage, pubsub_v1
from google.cloud.storage import Blob



def connectToStorageBucket(bucket_name, config):
    try:
        storage_client = storage.Client(project=config["GCPPROJECT"])
        print(f'Connected to "{bucket_name}"" bucket')
        print(f'Storage Client: {storage_client}')
    except Exception as e:
        print("Failed to connect to Google Cloud Storage")
        print(e)
    return storage_client


def listNewCSVName(bucket_name, storage_client, config):
    blobs = storage_client.list_blobs(bucket_name)
    print("4")
    print(blobs)
    print("5")
    for blob in blobs:
        print(blob.name)
        if f'{config["CLOUDSTORAGE"]["inputfolder"]}' in blob.name and ".csv" in blob.name:
            print("7")
            new_csv = getFileNameFromFilePath(blob.name)
            return new_csv


def getFileNameFromFilePath(file_path):
    split_file_path = file_path.split('/')
    length_of_list = len(split_file_path)
    file_name = split_file_path[length_of_list-1]
    print(f'FileName: {file_name}')
    return file_name



def addColumnsToCSV(file_name, bucket_name, config):
    vf_df = pd.read_csv(f'gs://{bucket_name}/{config["CLOUDSTORAGE"]["inputfolder"]}{file_name}')#I.e like the following: "gs://vf-europe-west2-test/Input/23Aug2022-12_36-WA-Campaign_63047c708607fbc1c8cfddee_0_0.csv"
    acs_df = vf_df
    acs_df['Channel'] = "WhatsApp"
    acs_df['Vendor'] = "ValueFirst"
    campaign_id_num = file_name.split(".csv")[0].split("Campaign")[1].split("_")[1]
    #print(campaign_id_num)
    acs_df['Campaign ID'] = f'ValueFirst {campaign_id_num}'
    print(acs_df)
    #print("")
    

def sendCSVToACS(file_location, storage_client, bucket_name, config):
    print(file_location + " Llllllllll")
    acs_url = config["ACS"]["url"]
    bucket = storage_client.get_bucket(bucket_name)
    print(bucket)
    blob = bucket.blob(file_location)
    print(blob)
    print("12")#BROKEN HERE AS OF LAST NIGHT
    print(f'THIS IS THE BLOB NAME: {blob.name}')
    #downloaded_blob = blob.download_as_string()
    #print(f'DOWNLOADED BLOB:  {downloaded_blob}')
    print("12.1")
    #blob = downloaded_blob.decode('utf-8')
    print("12.2")
    
    print("13")
    print(f'BLOB: {blob}')
    print("14")
    files = {"file": open(blob.name,'rb')}
    print(files)
    print("15")
    response = requests.post(acs_url, files=files)
    print(response.status_code)
    print(response.text)

def myBackgroundFunction(event_data, context):
    print(f'THE FOLLOWING IS THE METADATA ABOUT THE FILE: {context}')
    print(f'THE FOLLOWING IS THE EVENT DATA(FILE FROM GCS): {event_data}')
    try:
        #add relative path to the config
	    config_path = filePath=os.path.abspath(r'configs.yml')

	    #Open config file
	    with open(config_path,"r") as file:
		    try:
			    config = yaml.safe_load(file)
		    except yaml.YAMLError as exc:
			    print(exc)
			    exit(exc)
	    main(config)
    except Exception as ex:
        print(ex)

def main(config):
    print("BEFORE GOOGLE APP CREDENTIAL")
    #might not need the below
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f'{config["FILE"]["localdirectoryforcodeandfiles"]}{config["CLOUDSTORAGE"]["credentialkeyjsonpath"]}'
    print("BEFORE GOOGLE APP CREDENTIAL")
    print("THIS IS A CUSTOM LOG - HOPE YOU CAN SEE ON CLOUD FUNCTIONS LOGS")
    bucket_name = f'{config["SYSTEMS"]["source"]}-{config["LOCATION"]["region"]}-{config["ENV"]}'
    print(f'BucketName: {bucket_name}')
    print("2")
    storage_client = connectToStorageBucket(bucket_name, config)
    print("3")
    new_csv = listNewCSVName(bucket_name, storage_client, config)
    print (f'This is the new csv file in the folder: {new_csv}')
    print(type(new_csv))
    print("4")
    addColumnsToCSV(new_csv,bucket_name, config)
    print("finished")
    #Now need to send this new file to the http endpoint using request libary, and if successful, move the older dataframe csv value first send to an archive foldder
    sendCSVToACS("https://storage.googleapis.com/vf-europe-west2-test/Input/23Aug2022-12_36-WA-Campaign_63047c708607fbc1c8cfddee_0_0.csv", storage_client, bucket_name, config)
    
    



    
            

if __name__ == "__main__":
    try:
        #add relative path to the config
	    config_path = filePath=os.path.abspath(r'configs.yml')

	    #Open config file
	    with open(config_path,"r") as file:
		    try:
			    config = yaml.safe_load(file)
		    except yaml.YAMLError as exc:
			    print(exc)
			    exit(exc)
	    main(config)
    except Exception as ex:
        print(ex)
        