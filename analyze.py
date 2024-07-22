import os
import datetime
import requests
import json
import boto3
import pytz
import csv
from botocore.client import Config

# get current timestamp and display it
start_time = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
print(f"INFO\tAnalyzer started on {start_time.strftime('%d.%m.%Y %H:%M:%S')}")

# Define S3-compatible service details
endpoint_url = ''
access_key = ''
secret_key = ''
bucket_name = 'scheine-vereine-2024'

# Name of the target file
target = 'scheinevereine2024.csv'

### ### ### ### ### ### ### ### ### ### ### 

# Create a session using the S3-compatible service
session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    config=Config(signature_version='s3v4')
    )

# the results could be easily over 1000 objects
# in that case pagination is needed, this example should get them all!
def get_all_s3_objects(bucket_name, s3_client):
    paginator = s3_client.get_paginator('list_objects_v2')
    object_keys = []
    
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            object_keys.append(obj['Key'])

    if 'count.txt' in object_keys:
        object_keys.remove('count.txt')
        # remove my counter file for wordpress, otherwise the script will crash.
    
    return object_keys

# get now all those jsons
keys = get_all_s3_objects(bucket_name, s3_client)

print(f"INFO\tFound {len(keys)} objects in the bucket")

### ### ### ### ### ### ### ### ### ### ### 

with open(target, mode='w', newline='') as file:
    # open the chosen file with csv writer, insert the table head first.
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'totalBalance', 'redeemed', 'Customer_Registered', 'WishList', 'availableBalance', 'LatestOrder', 'disabled'])

    # go thru all keys, download it, get the required data and write it to the csv,
    # contuining to the next one. 
    for i, key in enumerate(keys):
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_content = response['Body'].read().decode('utf-8')
        data = json.loads(file_content)

        # the check for the field 'success' is needed, as if a 
        # download of 'main.py' failed it dropped a file just containing that it wasn't 
        # successful scraping and why. but no field data!
        # that datetime thing just reconstructs the format of the filename to human readable
        if data.get('success'):
            writer.writerow([
                datetime.datetime.strptime(key.split('.')[0], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                data['data']['totalBalance'], 
                data['data']['redeemed'], 
                data['data']['Customer_Registered'], 
                json.dumps(data['data']['WishList']), 
                data['data']['availableBalance'], 
                json.dumps(data['data']['LatestOrder']), 
                data['data']['disabled']
            ])
        else: 
            writer.writerow([
                datetime.datetime.strptime(key.split('.')[0], '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                '', # no totalBalance
                '', # no redeemed
                '', # no registration
                '', # no wishlist
                '', # no balance
                '', # no latest order
                '' # no one knows.
            ])
        # getting > 1000 files from a server takes time. Not an hour but enough that
        # a progress info might be helpful against the uncertainty if it works, or not.
        # especially as the script does not really care about error handling.
        # if your export fails mid run, delete the result, start over. 
        print(f"INFO\twritten {i+1} / {len(keys)}: {key}\r", end='', flush=True)

stop_time = datetime.datetime.now(pytz.timezone('Europe/Berlin'))
delta_time = stop_time - start_time

print(f"\nINFO\tAnalyzer finished on {stop_time.strftime('%d.%m.%Y %H:%M:%S')}, took {delta_time}")