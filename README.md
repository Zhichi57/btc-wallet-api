# BTC Wallet API

## Description

Backend application that will allow users to register, create own BTC wallets and
transfer BTC to other wallets inside the platform. Platform makes 1.5% profit from
Transactions between users

The following RESTful API endpoints are implemented:
- POST /users - creates user.Returns a token that will authenticate all other requests for this user.
- POST /wallets - create BTC wallet for the authenticated user. 1 BTC (or 100000000
satoshi) is automatically granted to the new wallet upon creation. User may register
up to 10 wallets. Returns wallet address and current balance in BTC and USD.
- GET /wallets/:address - returns wallet address and current balance in BTC and USD.
- POST /transactions - makes a transaction from one wallet to another. Transaction is free if transferred to own wallet.
Transaction costs 1.5% of the transferred amount (profit of the platform) if transferred to a wallet of another user.
- GET /transactions - returns user’s transactions
- GET /wallets/:address/transactions - returns transactions related to the wallet

Additional endpoint for administrator:
- GET /statistics - returns the total number of transactions and platform profit. Authenticated with hardcoded token.

## Installation
Download project  
```
git clone https://gitlab.com/Zhichi57/btc-wallet-api.git
cd btc-wallet-api  
```
Compile and run environment with docker-compose  
```
docker-compose up -d --build
```    
  
The service will be available at `127.0.0.1:8000`
