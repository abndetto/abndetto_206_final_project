import json
import requests 
from bs4 import BeautifulSoup
import time
import sqlite3
import os

# api keys and info
rapidapi_host = "movie-database-alternative.p.rapidapi.com"
rapidapi_key = "c8b4b8b8a5mshb6b8b2b2b2b2b2bp1b"



# setup database
db_name = "Practice_DB"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + "/" + db_name)
cur = conn.cursor()



# get list of movie titles from Rotten Tomatoes website
url = "https://editorial.rottentomatoes.com/guide/movies-100-percent-score-rotten-tomatoes/"

query = requests.get(url) 
soup = BeautifulSoup(query.text,"html.parser") 
title_list = []
results = soup.find_all('div', class_ = "col-sm-18 col-full-xs countdown-item-content")
for div in results:
    h2_tag = div.find('h2')
    if h2_tag:
        rspan = h2_tag.find("span")
        year = rspan.get_text(strip=True)
        year = int(year[1:-1])
        ra = h2_tag.find('a')
        title = ra.get_text(strip=True)
        movie_info = title, year
        title_list.append(movie_info)
                
# print(title_list)
# print(len(title_list))

def add_movies_to_database(title_list, conn, cur):
    added_count = 0
    cur.execute("CREATE TABLE IF NOT EXISTS Rotten_Tomatoes (title TEXT PRIMARY KEY, id INTEGER, year INTEGER)")
    cur.execute("SELECT MAX(id) FROM Rotten_Tomatoes")
    last_id = cur.fetchone()[0]
    last_id = 0 if last_id is None else last_id

    for tup in title_list:
        cur.execute("SELECT COUNT(*) FROM Rotten_Tomatoes WHERE title=?", (tup[0],))
        count = cur.fetchone()[0]

        if count == 0:
            last_id += 1
            cur.execute("INSERT INTO Rotten_Tomatoes (title, id, year) VALUES (?,?,?)", (tup[0], last_id, tup[1]))
            added_count += 1
            

        if added_count == 25:
            break

    conn.commit()
    print(added_count)
    return added_count

add_movies_to_database(title_list, conn, cur)   



# plug in move titles to movie api
def five_movies(title_list):
    return_dict = {}
    counter = 0

    for title in title_list:
        if counter < 4:
            url = f"https://movie-database-alternative.p.rapidapi.com/"

            query = {"s":title,"r":"json","page":"1"}

            headers = {
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": rapidapi_host
            }

            response = requests.get(url, headers=headers, params=query)
            data = json.loads(response.text)
            time.sleep(1)
            
            if "Search" in data.keys():
                if data['Search'][0]['Title'].lower() == title.lower():
                    return_dict[title] = {"imdbID":data['Search'][0]['imdbID'],"Year":data['Search'][0]['Year']}
                    print(return_dict)
                    counter += 1
                    continue
            else:
                print(f"the search title was {data}. the correct title was {title}")
                print("Movie not found")
                continue    
        else:
            break         
    print(return_dict)
    return return_dict


