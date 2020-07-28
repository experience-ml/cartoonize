import Algorithmia

with open("algo.txt", "r") as infile:
   client_key = infile.read()

client = Algorithmia.client(client_key)
algo = client.algo('tjdevworks/cartoonizer/2.2.2')
algo.set_options(timeout=300)

def api_request(input_file_uri):
    # API call for cartoonization.
    input = {"data_uri": input_file_uri,
            "data_type": 1,
            "datastore": ""
            }
    
    response = algo.pipe(input).result
    
    return response