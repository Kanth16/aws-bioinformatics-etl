import requests
import pymysql
import os
import json
import logging
import boto3
import xml.etree.ElementTree as ET

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS S3 Client
s3_client = boto3.client("s3")

# MySQL Database Configuration
RDS_HOST = "neurological-diseases.ckz6q8wguj2u.us-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "Devilcant123$"
RDS_DATABASE = "NeurologicalDiseases"

def lambda_handler(event, context):
    try:
        logger.info("✅ Lambda Started")
        
        # Access S3 Bucket
        bucket_name = os.environ.get("BUCKET_NAME", "dataextraction-myproject")
        logger.info(f"📂 Bucket Name: {bucket_name}")

        # Connect to MySQL
        try:
            connection = pymysql.connect(
                host=RDS_HOST,
                user=RDS_USER,
                password=RDS_PASSWORD,
                database=RDS_DATABASE,
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("✅ Connected to MySQL!")
        except Exception as db_error:
            logger.error(f"❌ Database Connection Failed: {str(db_error)}")
            return {"statusCode": 500, "body": f"Database Error: {str(db_error)}"}

        # Query the UniProt table
        with connection.cursor() as cursor:
            sql = f"SELECT DISTINCT SNPs FROM Omim WHERE SNPs IS NOT NULL AND Disease_Name='{event['Disease']}'"
            cursor.execute(sql)
            results = cursor.fetchall()

        # Extract and format SNP IDs
        results = [item['SNPs'].replace('rs', '') for item in results]
        for i in results:
            if ',' in i:
                temp = i.split(',')
                results.remove(i)
                results.extend(temp)
        logger.info(f"🔢 Found {len(results)} SNP IDs")

        # Close DB connection
        connection.close()

        # Fetch SNP details from NCBI API
        ncbi_results = []
        for snp_id in results:
            try:
                url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{snp_id}"
                logger.info(f"🔍 Fetching SNP ID: {snp_id}")

                response = requests.get(url, timeout=10)

                if response.status_code != 200:
                    logger.error(f"❌ API Error for {snp_id}: {response.status_code}")
                    continue

                snp_data = response.json()
                snp_info = {}
                snp_info["SNP"]= f"rs{snp_id}"
                snp_info["Alleles"]= []
                location = "N/A"
                chromosome_number = "N/A"

                # Extract chromosome & position
                for placement in snp_data.get("primary_snapshot_data", {}).get("placements_with_allele", []):
                    if placement.get("is_ptlp", False):  # Primary assembly
                        snp_info["NCBI ID"] = placement.get("seq_id", "N/A")
                        for allele in placement.get("alleles", []):
                            pos = allele.get("allele", {}).get("spdi", {}).get("position", "N/A")
                            ref = allele.get("allele", {}).get("spdi", {}).get("deleted_sequence", "N/A")
                            alt = allele.get("allele", {}).get("spdi", {}).get("inserted_sequence", "N/A")
                            if pos != "N/A":
                                snp_info["SNP Position"] = pos
                            if ref != "N/A" and alt != "N/A" and ref != alt:
                                snp_info["Alleles"].append(f"{ref}>{alt}")

                allele_annotation = snp_data.get("primary_snapshot_data", {}).get("allele_annotations", [])[0]
                # Extract Gene Name
                gene = allele_annotation.get('assembly_annotation',[])[0]['genes'][0]['locus']
                gene_id = allele_annotation.get('assembly_annotation', [])[0]['genes'][0]['id']
                gene_data_url=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id={gene_id}&rettype=fasta'
                gene_response=requests.get(gene_data_url)
                root = ET.fromstring(gene_response.text)
                for dl in root.findall(".//dl[@class='details']"):
                    for dt in dl.findall("dt"):
                        # print(dt.text)
                        # Check if 'dt' contains 'Annotation' and then find the next 'dd'
                        if "Annotation" in (dt.text or ''):
                            # The next sibling is likely a 'dd', found by index in the parent 'dl'
                            dd_index = list(dl).index(dt) + 1
                            if dd_index < len(dl):
                                dd = list(dl)[dd_index]
                                if dd.tag == 'dd':
                                    chromosome_number = dd.text.split(',')[0].split()[1]
                                    if chromosome_number.isdigit():
                                        chromosome_number = int(chromosome_number)
                                    else:
                                        chromosome_number = "N/A"
                        if "Location" in (dt.text or ''):
                            dd_index = list(dl).index(dt) + 1
                            if dd_index < len(dl):
                                dd = list(dl)[dd_index]
                                if dd.tag == 'dd':
                                    location = dd.text
                # print(type(gene_data_url))

                # Final Output
                snp_info.update( {
                    "SNP": f"rs{snp_id}",
                    "Gene_ID": gene_id,
                    "Chromosome Number": chromosome_number,
                    "Location": location
                })

                ncbi_results.append(snp_info)
                logger.info(f"✅ Processed SNP: {snp_info}")

            except Exception as api_error:
                logger.error(f"❌ Failed to process SNP {snp_id}: {str(api_error)}")
                continue

        logger.info(f"📊 Processed {len(ncbi_results)} SNP records")
        ncbi_results='\n'.join(json.dumps(record) for record in ncbi_results)
        file_key = f"Raw Data/NCBI/{event['Disease']}/data.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=ncbi_results,
            ContentType="application/json"
        )

        # Return JSON Response
        return {
            "statusCode": 200,
            "body": "Data Uploaded Successfully"
        }

    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        return {"statusCode": 500, "body": f"❌ Error: {str(e)}"}
