import os
import datetime
import requests
import json
import boto3
import pytz
from botocore.client import Config

# Get the current time in the specified timezone
current_time = datetime.datetime.now(pytz.timezone('Europe/Berlin'))

# Print info that the scraper has started with timestamp
print(f"INFO\tScraper started on {current_time.strftime('%d.%m.%Y %H:%M:%S')}")

# Define S3-compatible service details
endpoint_url = ''
access_key = ''
secret_key = ''
bucket_name = 'scheine-vereine-2024'
file_path = './soup.json'
count_name = './count.txt'
object_name = current_time.strftime('%Y%m%d_%H%M%S') + '.json'
# that object name is the timestamp in the format YYYYMMDD_HHMMSS.json
# please alter that to your needs, even if scraped hourly i want to know the exact timestamp

url = "https://scheinefuervereine.rewe.de/consumer-api/customer.php?action=get_club&id=YOURID"
# visit your redeem site and look in the url for the id

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=endpoint_url,
    config=Config(signature_version='s3v4')
    )

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("INFO\tData retrieved successfully")
    
    pretty_json = json.dumps(data, indent=4)

    ### fire the raw json to the s3 bucket ###

    # store the json to disk
    try:
        with open('soup.json', 'w') as file:
            file.write(pretty_json)
    except Exception as e:
        print(f'ERROR\tFailed to save data to disk: {e}')

    # upload the file to the S3 bucket
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f'INFO\tScraped data uploaded successfully to {bucket_name}/{object_name}')
    except Exception as e:
        print(f'ERROR\tFailed to upload file: {e}')

        # emergency save to disk, if upload fails in case S3 is fucked up
        try:
            with open('soup-' + object_name, 'w') as file:
                file.write(pretty_json)
            print(f'INFO\tData saved to disk as soup-{object_name}')
        except Exception as e:
            print(f'ERROR\tFailed to save data to disk: {e}')
    finally:
        # clean up by removing the file from disk
        os.remove(file_path)
        print(f'INFO\tClean up complete, exiting...')

    ### extract the amount of coupons for wordpress ###

    available_balance = data["data"]["availableBalance"]
    # maybe there's something else to do
    # count_path is configured with the s3 stuff, just how the file 
    # containing the amount is called. 

    try:
        with open(count_name, "w") as file:
            file.write(str(available_balance))
    except:
        print(f'ERROR\tFailed to save data to disk: {e}')
        # no emergency save as that is only relevant for an hour.
    
    # upload the file to the S3 bucket
    try:
        s3_client.upload_file(count_name, bucket_name, "count.txt")
        print(f'INFO\tScraped data uploaded successfully to {bucket_name}/{count_name}')
    except Exception as e:
        print(f'ERROR\tFailed to upload file: {e}')
    finally:
        # clean up by removing the file from disk
        os.remove(count_name)
        print(f'INFO\tClean up complete, exiting...')

else:
    print(f"ERROR\tFailed to retrieve data. Status code: {response.status_code}")