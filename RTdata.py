import json
import requests 
from bs4 import BeautifulSoup
import time
import sqlite3
import os

# api keys and info
rapidapi_host = "movie-database-alternative.p.rapidapi.com"
rapidapi_key = "21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02"

# setup database
db_name = "Practice_DB"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + "/" + db_name)
cur = conn.cursor()



# get list of movie titles from Rotten Tomatoes website using BeautifulSoup
url = "https://editorial.rottentomatoes.com/guide/essential-movies-to-watch-now/"

query = requests.get(url) 
soup = BeautifulSoup(query.text,"html.parser") 
title_list = []
results = soup.find_all('div', class_ = "col-sm-20 col-full-xs")
for div in results:
    h2_tag = div.find('h2')
    target_span = div.find('span', class_='tMeterScore')
    if h2_tag:
        rspan = h2_tag.find("span", class_="subtle start-year")
        year = rspan.get_text(strip=True)
        ra = h2_tag.find('a')
        title = ra.get_text(strip=True)
        score = target_span.get_text(strip=True)
        score = int(score[:-1])
        xyear = year[1:-1]
        movie_info = title, xyear, score
        title_list.append(movie_info)
                
# add movie titles, years, and local id to database
def add_rt_data_to_database(title_list, conn, cur):
    added_count = 0
    cur.execute("CREATE TABLE IF NOT EXISTS Rotten_Tomatoes (title TEXT PRIMARY KEY, id INTEGER, year INTEGER, score INTEGER)")
    cur.execute("SELECT MAX(id) FROM Rotten_Tomatoes")
    last_id = cur.fetchone()[0]
    last_id = 0 if last_id is None else last_id

    for tup in title_list:
        cur.execute("SELECT COUNT(*) FROM Rotten_Tomatoes WHERE title=?", (tup[0],))
        count = cur.fetchone()[0]

        if count == 0:
            last_id += 1
            cur.execute("INSERT INTO Rotten_Tomatoes (title, id, year, score) VALUES (?,?,?,?)", (tup[0], last_id, tup[1],tup[2]))
            added_count += 1

        if added_count == 25:
            break

    conn.commit()
    print(added_count)
    return added_count
for i in range(6):
    add_rt_data_to_database(title_list, conn, cur)   


