from nft_downloader import NFT_Downloader

key = "YOUR_ETHERSCAN_KEY"
link = "YOUR_INFURA_PROJECT_LINK"
addresses = ["0x521f9C7505005CFA19A8E5786a9c3c9c9F5e6f42", "0x36d16e0758D1B52c28c4579e12B9EfA0D23BAB29"]

directory = "C:\\SOME\\DIRECTORY\\"

downloader = NFT_Downloader(key, link)
downloader.download_nfts(addresses, directory)