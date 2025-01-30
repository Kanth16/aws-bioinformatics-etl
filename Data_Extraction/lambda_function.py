import json
import requests
from bs4 import BeautifulSoup


def lambda_handler(event, context):
    # TODO implement
    print("Hello")
# Making a GET request
    r = requests.get('https://thebiogrid.org/106848')

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')

    s = soup.find_all('a', class_='linkoutChip externalLinkout')
    for link in s:
        if "OMIM" in link.get_text():
            print(link['title'])
            return link['title']

    return {
        'statusCode': 200,
        'body': json.dumps('Hello World Lambda Deployed Successfully!')
    }
    
lambda_handler(1,2)
