# Scalability: Stock Exchange Matching Engine

## Overview

This project is about creating an exchange matching engine for a stock/commodities market. The engine matches buy and sell orders based on defined criteria and maintains accounts with unique identifiers and associated positions. The server software is designed to be scalable and robust, capable of handling multiple concurrent orders.

## Key Concepts

- **Symbol:** Identifier for a stock or commodity.
- **Position:** Symbol and amount owned, only allowing "long" positions (no short sales).
- **Account:** Unique ID, balance in USD, and positions held. Balances must never become negative.
- **Order:** Request to buy or sell a symbol with specified amount and limit price.
- **Open Order:** Status of an order when it is first placed.
- **Match Orders:** Process of matching buy and sell orders based on the symbol and compatible limit prices.
- **Executing an Order:** Adding money to the seller’s account and adjusting positions and shares in the buyer’s and seller’s accounts.
- **Canceling an Order:** Allows a user to cancel an open order, refunding the purchase price or returning shares.

## Server Requirements

1. **Initial State:** On startup, the server should have no symbols, accounts, or orders.
2. **Listening Port:** The server listens for incoming connections on port 12345.
3. **XML-based Communication:** Server receives commands in XML format, with the first line containing the length of the XML data.
4. **Order Creation and Cancellation:** Handles creation, execution, and cancellation of orders as per XML requests.
5. **Logging and Response:** Maintains a log of transactions and sends appropriate XML responses for each action.

## Scalability Testing

- The server's design focuses on scalability, particularly in terms of CPU core count.
- The project includes a write-up with graphs analyzing the server's throughput across different numbers of cores.

## Development Language

- The server can be written in any programming language or a combination of languages.

## Installation and Running

### Prerequisites
- Docker
  
### Installation
1. Clone the repository to your local machine:

```sh
git clone https://github.com/KoushikAS/HTTP_Caching_Proxy.git
cd HTTP_Caching_Proxy
```

### Running with Docker

1. Use Docker to build and run the containers.

```
docker-compose up -d
```

## Testing

There are two type of testing 

Functionality testing: Ensure the exchange matching  server returns the expected output

```
cd testing/
bash functionality-test.sh 

```

This will check for all the functionality testing and matches the output.
Note: Account creation output may differ if you run it multiple times. Please clear the database before running it


Load testing run: Ensures to flood the server with lot of request to stress test the server.

```
cd testing/
python3 loadtesting.py 

```

## Usage

- **Starting the Server:** Run using docker-compose; listens on port 12345.
- **Sending Requests:** Communicate with the server using XML-formatted messages according to the provided specifications.

## Contributions

This project was completed as part of an academic assignment with requirments provided requirments.pdf. Contributions were made solely by Koushik Annareddy Sreenath, Ryan Mecca, adhering to the project guidelines and requirements set by the course ECE-568 Engineering Robust Server Software 

## License

This project is an academic assignment and is subject to university guidelines on academic integrity and software use.

## Acknowledgments

Thanks to Brian Rogers and the course staff for providing guidance and support throughout the project.
