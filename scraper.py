import xml.etree.ElementTree as ET
import json
import requests
import re

# a simple scraper to get a list of PDB codes for all proteins in the PCBA database
# the proteins.xml input file can be accessed at https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1030,1379,1452,1454,1457,1458,1460,1461,1468,1469,1471,1479,1631,1634,1688,1721,2100,2101,2147,2242,2326,2451,2517,2528,2546,2549,2551,2662,2675,2676,411,463254,485281,485290,485294,485297,485313,485314,485341,485349,485353,485360,485364,485367,492947,493208,504327,504332,504333,504339,504444,504466,504467,504706,504842,504845,504847,504891,540276,540317,588342,588453,588456,588579,588590,588591,588795,588855,602179,602233,602310,602313,602332,624170,624171,624173,624202,624246,624287,624288,624291,624296,624297,624417,651635,651644,651768,651965,652025,652104,652105,652106,686970,686978,686979,720504,720532,720542,720551,720553,720579,720580,720707,720708,720709,720711,743255,743266,875,881,883,884,885,887,891,899,902,903,904,912,914,915,924,925,926,927,938,995/targets/ProteinGI,ProteinName,GeneID,GeneSymbol/XML

tree = ET.parse('./proteins.xml')
root = tree.getroot()

k = []
for child in root: 
    k.append( 
        { 
            'ProteinName': child.find('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}ProteinName').text, 
            'GI': child.find('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}GI').text, 
            'AID': child.find('{http://pubchem.ncbi.nlm.nih.gov/pug_rest}AID').text 
        } 
    ) 

for n in k: 
    if n.get('pdb_ids'): 
        continue 
    print(n['ProteinName']) 
    n['pdb_ids'] = [] 
    url = 'https://www.ncbi.nlm.nih.gov/structure?Db=structure&DbFrom=protein&Cmd=Link&LinkName=protein_structure&LinkReadableName=Structure&IdsFromResult={}'.format(n['GI']) 
    try: 
        r = requests.get(url)
        rtext = r.text
    except Exception: # connection error 
        n['pdb_ids'] = None 
        continue 
    if 'No items found.' in rtext: 
        n['pdb_ids'] = [None] 
        continue 
    if 'https://www.ncbi.nlm.nih.gov/Strucure/pdb/' in rtext: 
        pdb_code = r.text.split('<title>')[1][0:4]    
        n['pdb_ids'] = [pdb_code] 
        print('single') 
        continue 
    n['pdb_ids'] = [n[17:21] for n in re.findall('PDB ID: </dt><dd>.?.?.?.?</dd></dl>', rtext)] 

with open('proteins.json', 'w') as f:
    json.dump(k, f, indent=4, sort_keys=True)

# for n in k: 
#     if n.get('pdb_ids'): 
#         continue 
#     print(n['ProteinName']) 
#     n['pdb_ids'] = [] 
#     if os.path.exists('html/{}.html'.format(n['GI'])): 
#         with open('html/{}.html'.format(n['GI'])) as f: 
#             rtext = f.read() 
#     else: 
#         url = 'https://www.ncbi.nlm.nih.gov/structure?Db=structure&DbFrom=protein&Cmd=Link&LinkName=protein_structure&LinkReadableName=Structure&IdsFromResult={}'.format(n['GI']) 
#         try: 
#             r = requests.get(url) 
#             rtext = r.text 
#         except Exception: 
#             n['pdb_ids'] = None 
#             continue 
#     if 'No items found.' in rtext: 
#         n['pdb_ids'] = [None] 
#         continue 
#     if 'https://www.ncbi.nlm.nih.gov/Strucure/pdb/' in rtext: 
#         pdb_code = rtext.split('<title>')[1][0:4] 
#         n['pdb_ids'] = [pdb_code] 
#         print('single') 
#         continue 
#     n['pdb_ids'] = [n[17:21] for n in re.findall('PDB ID: </dt><dd>.?.?.?.?</dd></dl>', rtext)] 
