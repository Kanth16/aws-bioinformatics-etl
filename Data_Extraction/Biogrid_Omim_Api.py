import requests
from bs4 import BeautifulSoup
import pymysql
import os
import json
import boto3

# AWS S3 Client
s3_client = boto3.client("s3")

# MySQL Database Configuration
RDS_HOST = "neurological-diseases.ckz6q8wguj2u.us-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "Devilcant123$"
RDS_DATABASE = "NeurologicalDiseases"

def lambda_handler(event, context):
    try:
        # Access the environment variable
        print(os.environ.get("BUCKET_NAME"))
        bucket_name = os.environ.get("BUCKET_NAME", "dataextraction-myproject")


        print("Bucket Name:", bucket_name)  # Debugging

        if not bucket_name:
            return {"statusCode": 500, "body": "BUCKET_NAME environment variable is missing"}

        # Connect to MySQL
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ Connected to MySQL!")
        # Looping through links to find OMIM
        omim_link = {}

        # Query the UniProt table
        with connection.cursor() as cursor:
            sql = f"SELECT Biogrid_id FROM UniProt where Biogrid_ID is NOT NULL and Disease_Name='{event['Disease']}'"
            cursor.execute(sql)
            results = cursor.fetchall()
        print(type(results))
        results = [item['Biogrid_id'] for item in results]
        print(results)
        # Close the connection
        connection.close()
        for i in results:
            biogrid_url = f'https://thebiogrid.org/{i}'
            # Making a GET request
            response = requests.get(biogrid_url)

            # Parsing the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Finding all link elements with the specified class
            links = soup.find_all('a', class_='linkoutChip externalLinkout')
            for link in links:
                flag = False
                if "OMIM" in link.get_text():
                    omim_link[i] = link['title'].split()[1]
                    flag = True
                    break
                    # print(i,link['href'])  # Extract and return the URL
            if flag == False:
                omim_link[i] = "0"
        # print(omim_link)
        omim_out=[]
        for bid,omim in omim_link.items():
            if omim != "0":
                headers = {
                    "ApiKey": "vaZVEn2USSu1nXPeS0JF9A",
                    "Content-Type": "application/json"
                }
                response = requests.get(f'https://api.omim.org/api/entry/allelicVariantList?mimNumber={omim}&format=json',headers=headers)
                allelicVariant = response.json().get('omim', {}).get('allelicVariantLists', [{}])[0].get('allelicVariantList', [])
                # print(allelicVariant[0]['allelicVariant'])
                for i in allelicVariant:
                    temp={}
                    temp['Biogrid_id']=bid
                    temp['preferredTitle']=i['allelicVariant']['preferredTitle']
                    temp['mimNumber']=i['allelicVariant']['mimNumber']
                    if 'name' in i['allelicVariant']:
                        temp['Phenotype']=i['allelicVariant']['name']
                    if 'mutations' in i['allelicVariant']:
                        temp['mutations']=i['allelicVariant']['mutations']
                    # print(temp)
                    if 'dbSnps' in i['allelicVariant']:
                        temp['dbSnps']=i['allelicVariant']['dbSnps']
                    omim_out.append(temp)
        omim_out='\n'.join(json.dumps(record) for record in omim_out)
        print(omim_out)
        file_key = f"Raw Data/Omim/{event['Disease']}/data.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=omim_out,
            ContentType="application/json"
        )
        return {
            "statusCode": 200,
            "body": omim_out
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"❌ Error: {str(e)}"
        }