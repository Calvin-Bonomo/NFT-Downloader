from web3 import Web3, HTTPProvider
import requests
import json
import shutil
import time
import os

class NFT_Downloader:
    """This class provides a method by which you can download the images of non-fungible tokens from the blockchain. This class requires you to have an Etherscan api key and an Infura project (both freely available).
    
    Attributes
    ---
    DEFAULT_IPFS_PREFIX: str
        The link to the ipfs site

    Methods
    ---
    connect_to_web3()
        Connects to Web 3.0 using your infura link.
    get_abi(address)
        Gets the abi for the given wallet address.
    get_tokens(address)
        Get token IDs from the given wallet address.
    correct_link(link)
        A helper function which removes the 'ipfs://' prefix in some links.
    download_image(image_link, download_path, extension = "")
        Downloads the image at the specified link.
    get_image(image_link, download_path)
        A recursive function which searches through a page's JSON data to find the true link to an image.
    download_nfts(addresses, download_dir, download_cap = 100, create_dirs = True)
        Download NFTs from specified wallets.
    """

    DEFAULT_IPFS_PREFIX = 'https://ipfs.io/ipfs/'

    def __init__(self, etherscan_key: str, infura_link: str):
        """
        Parameters
        ---
        etherscan_key: str
            Your Etherscan API key
        infura_link: str
            Your link to the Infura network
        """

        self.etherscan_key = etherscan_key
        self.infura_link = infura_link

    def connect_to_web3(self) -> tuple:
        """Connects to Web 3.0 using your infura link.

        Must be called before calling download_nfts().

        Returns
        ---
        tuple
            A tuple where the first value is the connection to Web 3.0 and the second is the connection status
        """

        w3 = Web3(HTTPProvider(self.infura_link))
        return w3, w3.isConnected()

    def get_abi(self, address: str) -> tuple:
        """Gets the abi for the given wallet address.

        Parameters
        ---
        address: str
            Address of the creator of NFT that you want to download's wallet.

        Returns
        ---
        tuple
            A tuple containing the abi and status of the connection
        """

        req_link = 'https://api.etherscan.io/api?module=contract&action=getabi&address=' + address + '&apikey=' + self.etherscan_key
        req = requests.get(req_link)
        return json.loads(req.json()['result']), req.status_code == 200

    def get_tokens(self, address: str) -> list:
        """Returns a list of token IDs from the specified wallet address.

        Parameters
        ---
        address: str
            Address of the creator of NFT that you want to download's wallet.
        
        Returns
        ---
        list
            A list of token IDs
        """

        req_link = 'https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress=' + address + '&apikey=' + self.etherscan_key
        req = requests.get(req_link)
        if (req.status_code == 200):
            tokens = []
            transactions_json = req.json()['result']
            for transaction in transactions_json:
                tokens.append(int(transaction['tokenID']))
            return list(set(tokens))
        else:
            return []

    def correct_link(self, link: str) -> str:
        """A helper function which removes the 'ipfs://' prefix in some links.

        Parameters
        ---
        link: str
            A link which may contain the 'ipfs://' prefix.
        
        Returns
        ---
        str
            A new link
        """

        return link.replace('ipfs://', DEFAULT_IPFS_PREFIX)

    def download_image(self, image_link: str, download_path: str, extension: str = "") -> None:
        """Downloads the image at the specified link.

        Parameters
        ---
        image_link: str
            Link to the image to download.
        download_path: str
            Path to the directory where the image should be downloaded.
        extension: str
            An optional extension to add to the file.
        """

        req = requests.get(image_link, stream=True)
        if (req.status_code == 200):
            split_name = image_link.split('/')
            image_name = split_name[-2] + split_name[-1] + extension
            path = download_path + '\\' + image_name
            req.raw.decode_content = True
            if not os.path.isfile(path):
                with open(path, 'wb') as f:
                    print('Downloading ' + image_name + ' to directory ' + download_path + '.')
                    shutil.copyfileobj(req.raw, f)
            else:
                print('File ' + image_name + ' alrady exists.')
        else:
            print('Error: could not connect to ' + image_link + ', status code ' + str(req.status_code))

    def get_image(self, image_link: str, download_path: str) -> None:
        """A recursive function which searches through a page's JSON data to find the true link to an image.

        Parameters
        ---
        image_link: str
            Possible link to the image you want to download.
        download_path: str
            Path to the directory where the image should be downloaded.
        """

        req = requests.get(image_link, stream=True)
        if (req.status_code == 200):
            if (image_link.endswith('.png') or image_link.endswith('.jpg') or image_link.endswith('.jpeg')):
                download_image(correct_link(image_link), download_path)
                return
            else:
                try:
                    nftJSON = req.json()
                    jsonLink = str(nftJSON['image'])
                    return get_image(correct_link(jsonLink), download_path)
                except Exception:
                    download_image(correct_link(image_link), download_path, '.png')
        else:
            print('Error: could not connect to ' + image_link + ', status code ' + str(req.status_code))

    def download_nfts(self, addresses: list, download_dir: str, download_cap: int = 100, create_dirs: bool = True) -> bool:
        """Download NFTs from specified wallets.
        
        Parameters
        ---
        addresses: list
            A list of wallet addresses from which to download NFTs.
        download_dir: str
            Path to where files should be downloaded.
        download_cap: int, optional
            Maximum amount of NFTs which can be downloaded. If this value is 0, it will download every token it can (not recommended without a lot of storage space).
        create_dirs: bool, optional
            An optional setting which will create an additional directory for each address in addresses to save NFTs in.
        
        Returns
        ---
        bool
            Whether the NFTs successfully downloaded.
        """

        w3, connected = self.connect_to_web3()
        if not connected:
            print('Error: could not connect to Web3, please check your internet connection and try again.')
            return False

        # Iterate over all addresses
        for address in addresses:
            abi, got_abi = self.get_abi(address)
            if not got_abi:
                print('Error: could not get ABI from specified wallet ' + address + '.')
                continue
            tokens, got_tokens = self.get_tokens(address)
            if not got_tokens:
                print('Error: could not get token IDs from the specified wallet ' + address + '.')
                continue
            
            # Get the smart contract from the Ethereum blockchain
            address = Web3.toChecksumAddress(address)
            contract = w3.eth.contract(address=address, abi=abi)
            
            # Get the directory where nfts should be saved
            dir = download_dir
            if create_dirs:
                dir += '\\' + address
                if not os.path.isdir(dir):
                    os.mkdir(dir)

            # Figure out how many NFTs can be downloaded
            limit = download_cap
            if limit == 0 or limit > len(tokens):
                limit = len(tokens)
            
            # Try to download NFTs
            for i in range(limit):
                time.sleep(0.1) # Trying not to spam anything
                try:
                    image_link = str(contract.functions.imageURI(tokens[i]).call())

                    print('Attempting download of token ID #%i from %s.', tokens[i], image_link)
                    self.get_image(self.correct_link(image_link), dir)
                except Exception as e:
                    print(e)
        return True