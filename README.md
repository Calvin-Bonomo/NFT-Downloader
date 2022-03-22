# NFT-Downloader
A class which allows you to download NFTs to a local directory.

---
# How To
Create a new insatance of NFT_Downloader:
`downloader = NFT_Downloader(etherscan_key, infura_link)`,
and call download_nfts:
`download_nfts(accounts, download_dir, download_cap, create_dirs)`.

An example of this is shown in the example folder under `src`.
---
## Disclaimer
At the moment, only ERC-721 tokens which implement the optional, metadata interface provided as part of the ERC-721 standard. Thus, this class does not work for downloading NFTs like Cryptopunks and other non-standard NFTs.