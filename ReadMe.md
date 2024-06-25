# Football Data Collection

## Table of Contents

1. [Installation](#installation)
2. [Running](#running)
    - [Locally](#locally)
    - [Using Docker](#using-docker)
3. [Purpose of the Project](#purpose-of-the-project)
4. [Contents](#contents)



## Installation
### Prerequisites
- Python 3.9
- Docker

### Running
Clone the repo: git clone https://github.com/SlaterJoseph/FootballStockMarketDataCollection
Create a properties.yaml file in the root directory
- Add property: full_reset_password: 123abc (Needed for full reset route)

#### Locally
Create a virtual env: python -m venv venv
Activate the virtual env: 
- Windows: venv\Scripts\activate
- Unix: source venv/bin/activate
Install dependencies: pip install -r app/requirements.txt

#### Using Docker
To create the Docker Image navigate to the /app directory  
After run these commands in succession
- docker build -t fb-data-collection .
- docker run -d -p 5000:5000 fb-data-collection

## Purpose of the project
This is one component of a larger project. 
Here is where NFL player and team data is collected and preprocessed.
The data is to be used by an AI inorder to predict player performances for upcoming games

## Contents
Inside the project contains the CSVs from the 2021,2022, and 2023 seasons
