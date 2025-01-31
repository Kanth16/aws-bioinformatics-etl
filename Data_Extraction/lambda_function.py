import json
import requests
from bs4 import BeautifulSoup
import subprocess


import os
import json
import requests
import boto3

# AWS S3 Client
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    print(type(event))
    API_URL = f"https://rest.uniprot.org/uniprotkb/search?query={event['Disease']}"

    # Access the environment variable
    bucket_name = os.environ.get("BUCKET_NAME", "dataextraction-myproject")


    print("Bucket Name:", bucket_name)  # Debugging

    if not bucket_name:
        return {"statusCode": 500, "body": "BUCKET_NAME environment variable is missing"}

    response = requests.get(API_URL)

    if response.status_code == 200:
        json_data = response.json()

        file_key = f"Raw Data/{event['Disease']}/Uniprot.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(json_data, indent=4),
            ContentType="application/json"
        )

        return {"statusCode": 200, "body": "File uploaded successfully"}

    return {"statusCode": response.status_code, "body": "Failed to fetch API data"}
