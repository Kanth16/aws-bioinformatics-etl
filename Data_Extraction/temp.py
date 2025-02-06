import requests
import json
import xml.etree.ElementTree as ET

snp_id = "199476119" # "1554716504"  # Remove "rs" prefix for API call
url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{snp_id}"

response = requests.get(url)

if response.status_code == 200:
    snp_data = response.json()
else:
    print(f"Error: {response.status_code}")
    exit()

# Extract SNP ID
snp_id = snp_data.get("refsnp_id", "N/A")

# Extract Chromosome and Position
chromosome = "N/A"
position = "N/A"
alleles = []

for placement in snp_data.get("primary_snapshot_data", {}).get("placements_with_allele", []):
    if placement.get("is_ptlp", False):  # Primary assembly
        chromosome = placement.get("seq_id", "N/A")  # Chromosome
        for allele in placement.get("alleles", []):
            spdi = allele.get("allele", {}).get("spdi", {})
            ref = spdi.get("deleted_sequence", "N/A")  # Reference allele
            alt = spdi.get("inserted_sequence", "N/A")  # Alternate allele
            pos = spdi.get("position", "N/A")  # SNP Position
            if pos != "N/A":
                position = pos  # Update position
            if ref != "N/A" and alt != "N/A" and ref != alt:
                alleles.append(f"{ref}>{alt}")  # Format allele change (e.g., T>A)


# gene_id = spdi['primary_snapshot_data']['allele_annotations'][0]['assembly_annotation'][0]['genes'][0]['id']
allele_annotation = snp_data.get("primary_snapshot_data", {}).get("allele_annotations", [])[0]
# Extract Gene Name
gene = allele_annotation.get('assembly_annotation',[])[0]['genes'][0]['locus']
gene_id = allele_annotation.get('assembly_annotation', [])[0]['genes'][0]['id']
gene_data_url=f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id={gene_id}&rettype=fasta'
gene_response=requests.get(gene_data_url)
root = ET.fromstring(gene_response.text)
location = "N/A"
for dl in root.findall(".//dl[@class='details']"):
    for dt in dl.findall("dt"):
        print(dt.text)
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
print(type(gene_data_url))

# Final Output
snp_info = {
    "SNP": f"rs{snp_id}",
    "Chromosome": chromosome,
    "Position": position,
    "Alleles": alleles,  # List of allele variations
    "Gene":gene,
    "Gene_ID": gene_id,
    "Chromosome Number": chromosome_number,
    "Location": location
}

# Print Extracted Data
print(json.dumps(snp_info, indent=4))
