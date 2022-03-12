from xml.etree.ElementTree import tostring
from web3 import Web3, HTTPProvider
import requests
import json
import shutil
import time
import os
import sys

FUNC_MATCHES = ['image', 'ipfs', 'uri']
DEFAULT_IPFS_PREFIX = "https://ipfs.io/ipfs/"

def handle_args():
    args = sys.argv[1:]
    ethKey = args[args.index('-ethKey') + 1]
    nftDir = args[args.index('-nftDir') + 1]
    nftWallets = args[args.index('-nftWallets') + 1]
    infuraURL = args[args.index('-infuraURL') + 1]
    nftCap = args[args.index('-nftCap') + 1]
    return ethKey, nftDir, nftWallets, infuraURL, int(nftCap)

def print_error(message: str):
    print(("Error: " + message))

def get_etherscan_key(keyPath: str) -> str:
    keyFile = open(keyPath, 'r')
    key = keyFile.readline()
    keyFile.close()
    return key

def connect_to_infura(myLink: str):
    w3 = Web3(HTTPProvider(myLink))
    return w3, w3.isConnected()

def get_wallets(walletsPath: str):
    walletsFile = open(walletsPath, 'r')
    walletsData = walletsFile.read()
    walletsFile.close()

    wallets = walletsData.split('\n')
    return wallets

def get_infura_url(infuraPath: str) -> str:
    infuraFile = open(infuraPath, 'r')
    infuraURL = infuraFile.readline()
    infuraFile.close()
    return infuraURL

def get_address_abi(contractWallet: str, etherscanKey: str):
    getabiLink = 'https://api.etherscan.io/api?module=contract&action=getabi&address=' + contractWallet + '&apikey=' + etherscanKey
    req = requests.get(getabiLink)
    status = req.status_code == 200
    return json.loads(req.json()['result']), status

def get_address_token_ids(contractWallet: str, etherscanKey: str):
    tokenIDsLink = 'https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress=' + contractWallet + '&apikey=' + etherscanKey
    req = requests.get(tokenIDsLink)
    if (req.status_code == 200):
        tokenIDs = []
        transactionsJSON = req.json()['result']
        for transaction in transactionsJSON:
            tokenIDs.append(int(transaction['tokenID']))
        return list(set(tokenIDs)), True
    else:
        return [], False

def correct_link(link: str) -> str:
    return link.replace('ipfs://', DEFAULT_IPFS_PREFIX)

def download_image(imageLink: str, downloadTo: str, extension = ""):
    req = requests.get(imageLink, stream=True)
    if (req.status_code == 200):
        splitImageName = imageLink.split('/')
        imageName = splitImageName[-2] + splitImageName[-1] + extension
        req.raw.decode_content = True
        with open((downloadTo + '\\' + imageName), 'wb') as f:
            shutil.copyfileobj(req.raw, f)
    else:
        print_error("could not connect to " + imageLink + " status code " + str(req.status_code))

def get_image(imageLink: str, downloadTo: str):
    req = requests.get(imageLink, stream=True)
    if (req.status_code == 200):
        if (imageLink.endswith('.png') or imageLink.endswith('.jpg') or imageLink.endswith('.jpeg')):
            download_image(correct_link(imageLink), downloadTo)
            return
        else:
            try:
                nftJSON = req.json()
                jsonLink = str(nftJSON['image'])
                get_image(correct_link(jsonLink), downloadTo)
            except Exception:
                download_image(correct_link(imageLink), downloadTo, '.png')
    else:
        print_error("could not connect to " + imageLink + ", status code " + str(req.status_code))
    
def main():
    keyPath, saveDir, walletsPath, infuraPath, nftCap = handle_args()

    infuraLink = get_infura_url(infuraPath)

    w3, isConnected = connect_to_infura(infuraLink)

    if (not isConnected):
        print_error("could not connect to " + infuraLink)
        return
    
    key = get_etherscan_key(keyPath)

    wallets = get_wallets(walletsPath)

    for wallet in wallets:
        dir = saveDir + '\\' + str(wallet)
        if not os.path.isdir(dir):
            os.mkdir(dir)

        abi, abiWorked = get_address_abi(wallet, key)
        if (not abiWorked):
            print_error("could not get abi from account " + wallet)
            return

        tokenIDs, tokenIDsWorked = get_address_token_ids(wallet, key)
        if (not tokenIDsWorked):
            print_error("could not get token ids from account " + wallet)
            return

        wallet = Web3.toChecksumAddress(wallet)
        contract = w3.eth.contract(address=wallet, abi=abi)

        if nftCap == 0:
            print("Attempting to download " + str(len(tokenIDs)) + " nft(s).")
        else:
            print("Attempting to download " + str(nftCap) + " nft(s).")
        i = 0
        for tokenID in tokenIDs:
            if i >= nftCap:
                break
            time.sleep(0.1)
            
            try:
                tokenLink = contract.functions.tokenURI(tokenID).call()
                tokenLink = str(tokenLink)

                print("Downloading token ID #" + str(tokenID) + " from " + tokenLink)
                get_image(correct_link(tokenLink), dir)
                i += 1
            except Exception as e:
                print(e)

if __name__ == '__main__':
    main()