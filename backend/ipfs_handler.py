import os
import requests

PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_API_SECRET = os.getenv("PINATA_SECRET_API_KEY")  # Fixed

def upload_to_ipfs(file_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET
    }

    with open(file_path, "rb") as f:
        files = {
            'file': (os.path.basename(file_path), f)
        }
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()

    ipfs_hash = response.json()['IpfsHash']
    return ipfs_hash

def fetch_from_ipfs(cid):
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def test_pinata_connection():
    url = "https://api.pinata.cloud/data/testAuthentication"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_API_SECRET
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return True, "Successfully connected to Pinata API"
    except requests.exceptions.HTTPError as errh:
        return False, f"HTTP Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return False, f"Connection Error: {errc}"
    except requests.exceptions.Timeout as errt:
        return False, f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return False, f"Request Exception: {err}"
