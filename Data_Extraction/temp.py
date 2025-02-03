# import json

# def read_json_basic(file_path):
#     with open(file_path, 'r') as file:
#         data = json.load(file)
#         final_json={}
#         for i in range(len(data['results'])):
#             flag=0
#             print('primaryAccession:',data['results'][i]['primaryAccession'])
#             print('uniProtkbId:',data['results'][i]['uniProtkbId'])
#             print('scientificName:',data['results'][i]['organism']['scientificName'])
#             print(data['results'][i]['genes'][0]['geneName']['value']) 
#             print('recommendedName:',data['results'][i]['proteinDescription']['recommendedName']['fullName']['value'])
#             if('alternativeNames' in data['results'][i]['proteinDescription']):
#                 for j in range(len(data['results'][i]['proteinDescription']['alternativeNames'])):
#                     print(data['results'][i]['proteinDescription']['alternativeNames'][j]['fullName']['value'],"  ",end="")
#                 print()
#             for k in range(len(data['results'][i]['uniProtKBCrossReferences'])):
#                 if (data['results'][i]['uniProtKBCrossReferences'][k]['database'] == "BioGRID"):
#                     print("BioGrid ID: ",data['results'][i]['uniProtKBCrossReferences'][k]['id'])
#                     flag=1
#                     break
#     return data

# read_json_basic(r'D:\Dump\Project files\Uniprot_Alzimer.json')
# {106616: '602192', 106845: '107741', 106848: '104760', 107889: '116840', 107995: '126660', 
#  108481: '601819', 109079: '600395', 109186: '606784', 109187: '605004', 110308: '157140', 
#  110631: '516000', 110632: '516001', 111021: '602601', 111528: '600658', 111642: '104311', 
#  111643: '600759', 112506: '163890', 112536: '602005', 114186: '603610', 115629: '605414', 
#  115809: '605712', 116550: '611321', 117173: '615698', 124143: '610004'}

import requests
from bs4 import BeautifulSoup
import json

def get_omim_link(url):
    omim_link = {106616: '602192'}
    # , 106845: '107741', 106848: '104760', 107889: '116840', 107995: '126660'}
    # Making a GET request
    response = requests.get(url)

    # Parsing the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Finding all link elements with the specified class
    links = soup.find_all('a', class_='linkoutChip externalLinkout')
    # Looping through links to find OMIM
    for link in links:
        if "OMIM" in link.get_text():
            flag = False
            print(link['title'].split()[1])
            # return link['href']  # Extract and return the URL
    # if flag == False:
    #     return link['title'].split()[1]
    headers = {
    "ApiKey": "vaZVEn2USSu1nXPeS0JF9A",
    "Content-Type": "application/json"
    }
    # print(response.json()['omim']['allelicVariantLists'][0]['allelicVariantList'][0])
    omim_out=[]
    for bid,omim in omim_link.items():
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
    # print(json.dumps(omim_out, indent=4))
    return "OMIM link not found"

# URL of the BioGRID page
biogrid_url = 'https://thebiogrid.org/106848'

# Fetching the OMIM link
omim_link = get_omim_link(biogrid_url)
print("OMIM Link:", omim_link)
