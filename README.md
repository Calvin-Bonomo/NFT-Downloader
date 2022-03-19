# NFT-Downloader
A simple tool which lets you download nfts. It does require you to have an Etherscan api key and one from Infura as well.

There are 5 required command line arguments that must be used when running this program:
- `-ethKey`: The path to a .txt file with your Etherscan api key in it.
- `-nftDir`: The directory where you want nfts to be stored.
- `-nftWallets`: The path to a .txt file with a wallet address on each line.
- `-infuraURL`: The path to a .txt with your Infura URL copied into it.
- `-nftCap`: The number of NFTs you want to download per wallet.

---
## Disclaimer
At the moment, only ERC-721 tokens which implement the optional, metadata interface provided as part of the ERC-721 standard. Thus, this program does not work for downloading NFTs like Cryptopunks and other non-standard NFTs.