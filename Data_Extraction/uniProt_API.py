import os
import json
import requests
import boto3
from bs4 import BeautifulSoup
import subprocess

# AWS S3 Client
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    print(type(event))
    API_URL = f"https://rest.uniprot.org/uniprotkb/search?query={event['Disease']}"

    # Access the environment variable
    print(os.environ.get("BUCKET_NAME"))
    bucket_name = os.environ.get("BUCKET_NAME", "dataextraction-myproject")


    print("Bucket Name:", bucket_name)  # Debugging

    if not bucket_name:
        return {"statusCode": 500, "body": "BUCKET_NAME environment variable is missing"}

    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        results_list = []

        for i in range(len(data['results'])):
            entry = {}
            entry['primaryAccession'] = data['results'][i]['primaryAccession']
            entry['uniProtkbId'] = data['results'][i]['uniProtkbId']
            entry['scientificName'] = data['results'][i]['organism']['scientificName']
            entry['recommendedName'] = data['results'][i]['proteinDescription']['recommendedName']['fullName']['value']
            entry['Gene'] = data['results'][i]['genes'][0]['geneName']['value']
            # Alternative Names
            if 'alternativeNames' in data['results'][i]['proteinDescription']:
                entry['alternativeNames'] = [
                    name['fullName']['value'] for name in data['results'][i]['proteinDescription']['alternativeNames']
                ]
            
            # BioGRID ID
            entry['BioGRID_ID'] = None
            for k in range(len(data['results'][i]['uniProtKBCrossReferences'])):
                if data['results'][i]['uniProtKBCrossReferences'][k]['database'] == "BioGRID":
                    entry['BioGRID_ID'] = data['results'][i]['uniProtKBCrossReferences'][k]['id']
                    break

            results_list.append(entry)

        # Convert to JSON
        json_output = '\n'.join(json.dumps(record) for record in results_list)

        print(json_output)
        file_key = f"Raw Data/Uniprot/{event['Disease']}.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json_output,
            ContentType="application/json"
        )

        return {"statusCode": 200, "body": "File uploaded successfully"}

    return {"statusCode": response.status_code, "body": "Failed to fetch API data"}