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

# inputs: list of movie tuples (title, year made, rotten tomato score), database connection object, database cursor object
# outputs: returns the number of movies added to the database

# explanation: add_rt_to_database takes a list of movie tuples and database connection and curser objects and adds 
# the movie information to a database. First, it creates table "Rotten_Tomatoes" For each movie, it checks if the movie 
# already exists in the database. If the movie does not exist, it adds the movie to the database and increases the added_count 
# varibale by one. The process repeats until the added_count variable reaches 25, then the function quits. The function returns 
# the number of movies added to the database.
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

# add Rotten Tomatoes data to database
add_rt_data_to_database(title_list, conn, cur)

