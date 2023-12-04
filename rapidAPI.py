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

# plug in move titles to movie api
def create_rapid_api_json():
    if os.path.exists('output.json'):
        with open('output.json', 'r') as json_file:
            return_dict = json.load(json_file)
        return return_dict
    else:
        return_dict = {}  
        title_list = []        
        cur.execute('SELECT title FROM Rotten_Tomatoes')
        for rval in cur:
            rx = rval[0]
            title_list.append(rx)

        for title in title_list:
            import requests

            url = "https://movie-database-alternative.p.rapidapi.com/"

            query = {"s": title,"r":"json","page":"1"}

            headers = {
                "X-RapidAPI-Key": "21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02",
                "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=query)
            data = json.loads(response.text)
            time.sleep(1)
            
            if "Search" in data.keys():
                if data['Search'][0]['Title'].lower() == title.lower():
                    return_dict[title] = {"imdbID":data['Search'][0]['imdbID'],"Year":data['Search'][0]['Year']}
                    url = "https://movie-database-alternative.p.rapidapi.com/"
                    querystring = {"r":"json","i":data['Search'][0]['imdbID']}
                    headers = {
                        "X-RapidAPI-Key": "21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02",
                        "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
                    }
                    response = requests.get(url, headers=headers, params=querystring)
                    data = json.loads(response.text)
                    return_dict[data["Title"]] = {"imdbID":None,"Year":None,"Rated":None,"Released":None,"Runtime":None,"Genre":None,"Country":None,"Awards":None,"BoxOffice":None,"imdbRating":None,"Metascore":None}
                    return_dict[data["Title"]] = {"imdbID":data['imdbID'],"Year":int(data['Year']),"Rated":data['Rated'],"Released":data['Released'],"Runtime":data['Runtime'].split(" ")[0],"Genre":data['Genre'],"Country":data['Country'],"Awards":data['Awards'],"BoxOffice":data['BoxOffice'],'imdbRating':data['imdbRating'],'Metascore':data['Metascore']}
            else:
                print(f"the search title was {data}. the correct title was {title}")
                print("Movie not found")
        
        file_path = 'output.json'
        with open(file_path, 'w') as json_file:
            json.dump(return_dict, json_file, indent=4)
            
        return return_dict

rapid_api_data = create_rapid_api_json()
# print(len(rapid_api_data))

def set_up_types_tables(json_data, cur, conn):
    # create genre table
    genre_list = []
    for movie in json_data.keys():
        if "Genre" in json_data[movie].keys():
            if json_data[movie]["Genre"] != None:
                if "," in json_data[movie]["Genre"]:
                    movie_genre_list = json_data[movie]["Genre"].split(",")
                    movie_genre = movie_genre_list[0]
                else:
                    movie_genre = json_data[movie]["Genre"]
                if movie_genre not in genre_list:
                    genre_list.append(movie_genre)
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Genres (id INTEGER PRIMARY KEY, genre TEXT UNIQUE)"
    )
    for i in range(len(genre_list)):
        cur.execute(
            "INSERT OR IGNORE INTO Genres (id,genre) VALUES (?,?)", (i, genre_list[i])
        )
    
    # create rated table
    rated_list = []
    for movie in json_data.keys():
        if "Rated" in json_data[movie].keys():
            if json_data[movie]["Rated"] != None:
                movie_rating = json_data[movie]["Rated"]
                if movie_rating not in rated_list:
                    rated_list.append(movie_rating)
    cur.execute(
        "CREATE TABLE IF NOT EXISTS Rated (id INTEGER PRIMARY KEY, rating TEXT UNIQUE)"
    )
    for i in range(len(rated_list)):
        cur.execute(
            "INSERT OR IGNORE INTO Rated (id,rating) VALUES (?,?)", (i, rated_list[i])
        )
        
    conn.commit()
    
    # create country table
    country_list = []
    for movie in json_data.keys():
        if "Country" in json_data[movie].keys():
            if json_data[movie]["Country"] != None:
                if "," in json_data[movie]["Country"]:
                    m_country_list = json_data[movie]["Country"].split(",")
                    m_country = m_country_list[0]
                else:
                    m_country = json_data[movie]["Country"]
                if m_country not in country_list:
                    country_list.append(m_country)
    cur.execute(
        "CREATE TABLE IF NOT EXISTS MovieCountries (id INTEGER PRIMARY KEY, country TEXT UNIQUE)"
    )
    for i in range(len(country_list)):
        cur.execute(
            "INSERT OR IGNORE INTO MovieCountries (id,country) VALUES (?,?)", (i, country_list[i])
        )

set_up_types_tables(rapid_api_data, cur, conn)

def add_rapidapi_data_to_database(movie_dict, conn, cur):
    added_count = 0
    cur.execute("CREATE TABLE IF NOT EXISTS Rapid_API (title TEXT PRIMARY KEY, id INTEGER, year INTEGER, rated TEXT, released TEXT, runtime INTEGER, genre TEXT, country TEXT, awards TEXT, boxoffice TEXT, imdbRating INTEGER, metascore INTEGER)")
    cur.execute("SELECT MAX(id) FROM Rapid_API")
    last_id = cur.fetchone()[0]
    last_id = 0 if last_id is None else last_id

    for title in movie_dict.keys():
        if "imdbID" in movie_dict[title].keys() and "Year" in movie_dict[title].keys() and "Rated" in movie_dict[title].keys() and "Released" in movie_dict[title].keys() and "Runtime" in movie_dict[title].keys() and "Genre" in movie_dict[title].keys() and "Country" in movie_dict[title].keys() and "Awards" in movie_dict[title].keys() and "BoxOffice" in movie_dict[title].keys() and "imdbRating" in movie_dict[title].keys() and "Metascore" in movie_dict[title].keys():
            cur.execute("SELECT COUNT(*) FROM Rapid_API WHERE title=?", (title,))
            count = cur.fetchone()[0]

            if count == 0:
                if "," in movie_dict[title]['Genre']:
                    mgenre = movie_dict[title]['Genre'].split(",")[0]
                else:
                    mgenre = movie_dict[title]['Genre']
                cur.execute('SELECT id FROM Genres WHERE genre = ?', (mgenre,))
                genre = cur.fetchone()
                if genre != None:
                    if "," in genre:
                        genre = genre.split(",")[0]
                        genre = int(genre[0])
                    else:
                        genre = int(genre[0])
                else:
                    pass
                
                cur.execute('SELECT id FROM Rated WHERE rating = ?', (movie_dict[title]['Rated'],))
                rating = cur.fetchone()
                if rating != None:
                    rating = int(rating[0])
                else:
                    pass
                
                if "," in movie_dict[title]['Country']:
                    mcountry = movie_dict[title]['Country'].split(",")[0]
                else:
                    mcountry = movie_dict[title]['Country']
                cur.execute('SELECT id FROM MovieCountries WHERE country = ?', (mcountry,))
                country = cur.fetchone()
                if country != None:
                    if "," in country:
                        country = country.split(",")[0]
                        country = int(country[0])
                    else:
                        country = int(country[0])
                else:
                    pass
                last_id += 1
                try:
                    cur.execute("INSERT INTO Rapid_API (title, id, year, rated, released, runtime, genre, country, awards, boxoffice,imdbRating,metascore) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (title, last_id, movie_dict[title]['Year'], rating, movie_dict[title]['Released'], movie_dict[title]['Runtime'], genre, country, movie_dict[title]['Awards'], movie_dict[title]['BoxOffice'],movie_dict[title]['imdbRating'],movie_dict[title]['Metascore']))
                    added_count += 1
                except:
                    KeyError
                    pass
            

        if added_count == 25:
            break

    conn.commit()
    print(added_count)
    return added_count

add_rapidapi_data_to_database(rapid_api_data, conn, cur)
    
    