import json

def read_json_basic(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        final_json={}
        for i in range(len(data['results'])):
            flag=0
            print('primaryAccession:',data['results'][i]['primaryAccession'])
            print('uniProtkbId:',data['results'][i]['uniProtkbId'])
            print('scientificName:',data['results'][i]['organism']['scientificName'])
            print(data['results'][i]['genes'][0]['geneName']['value']) 
            print('recommendedName:',data['results'][i]['proteinDescription']['recommendedName']['fullName']['value'])
            if('alternativeNames' in data['results'][i]['proteinDescription']):
                for j in range(len(data['results'][i]['proteinDescription']['alternativeNames'])):
                    print(data['results'][i]['proteinDescription']['alternativeNames'][j]['fullName']['value'],"  ",end="")
                print()
            for k in range(len(data['results'][i]['uniProtKBCrossReferences'])):
                if (data['results'][i]['uniProtKBCrossReferences'][k]['database'] == "BioGRID"):
                    print("BioGrid ID: ",data['results'][i]['uniProtKBCrossReferences'][k]['id'])
                    flag=1
                    break
        
        # results_list = []

        # for i in range(len(data['results'])):
        #     entry = {}
        #     entry['primaryAccession'] = data['results'][i]['primaryAccession']
        #     entry['uniProtkbId'] = data['results'][i]['uniProtkbId']
        #     entry['scientificName'] = data['results'][i]['organism']['scientificName']
        #     entry['recommendedName'] = data['results'][i]['proteinDescription']['recommendedName']['fullName']['value']

        #     # Alternative Names
        #     if 'alternativeNames' in data['results'][i]['proteinDescription']:
        #         entry['alternativeNames'] = [
        #             name['fullName']['value'] for name in data['results'][i]['proteinDescription']['alternativeNames']
        #         ]
            
        #     # BioGRID ID
        #     entry['BioGRID_ID'] = None
        #     for k in range(len(data['results'][i]['uniProtKBCrossReferences'])):
        #         if data['results'][i]['uniProtKBCrossReferences'][k]['database'] == "BioGRID":
        #             entry['BioGRID_ID'] = data['results'][i]['uniProtKBCrossReferences'][k]['id']
        #             break

        #     results_list.append(entry)

        # # Convert to JSON
        # json_output = json.dumps(results_list, indent=4)
        # print(json_output)

    return data

read_json_basic(r'D:\Dump\Project files\Uniprot_Alzimer.json')