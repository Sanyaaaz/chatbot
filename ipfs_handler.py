import requests
import os

def upload_to_ipfs(file_path):
    token = os.getenv("WEB3_STORAGE_TOKEN")
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.web3.storage/upload',
            headers={
                'Authorization': f'Bearer {token}'
            },
            files={'file': (os.path.basename(file_path), f)}
        )
    response.raise_for_status()
    cid = response.json()['cid']
    return cid

def fetch_from_ipfs(cid):
    url = f"https://{cid}.ipfs.dweb.link"
    return requests.get(url).json()
