import requests
import json

# RT_dict = from file RTdata.py 
title_list = ['No Bears', 'Happening', 'Marcel the Shell with Shoes On']
for title in title_list:
    url = f"https://movie-database-alternative.p.rapidapi.com/"

    query = {"s":title,"r":"json","page":"1"}

    headers = {
        "X-RapidAPI-Key": "21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02",
        "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=query)

    print(response.json())
    print("-------")
    print("-------")
    print("-------")
    print("-------")
    print("-------")