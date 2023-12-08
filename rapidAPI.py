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

# create_rapid_api_json creates checks if a json file containing the movie information exists. 
# if the json file exists, it opens the file and returns the contents as a dictionary.
# if the json file does not exist, it opens the PracticeDB database and runs each movie title throug RapidAPI.
# If the query finds a match, the movies IMDB ID is returned and rerun through the same api. This second query 
# returns the movies year, rating, runtime, genre, country, awards, box office, IMDB rating, and metascore. This data 
# the saved to a created json file and the contents are returend by the function.
# Inputs: api key, database cursor object
# Outputs: json data as a dictionary (containing movie title as key and movie information as values)
def create_rapid_api_json(api_key = "21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02", cur = cur):
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
                        "X-RapidAPI-Key": api_key,
                        "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
                    }
                    response = requests.get(url, headers=headers, params=querystring)
                    data = json.loads(response.text)
                    cur.execute('SELECT id FROM Rotten_Tomatoes WHERE title = ?', (data['Title'],))
                    RiD = cur.fetchone()
                    print(data['Title'])
                    print(RiD)
                    if RiD != None:
                        RiD = int(RiD[0])
                        return_dict[RiD] = {"imdbID":None,"Rated":None,"Released":None,"Runtime":None,"Genre":None,"Country":None,"Awards":None,"BoxOffice":None,"imdbRating":None,"Metascore":None}
                        return_dict[RiD] = {"imdbID":data['imdbID'],"Rated":data['Rated'],"Released":data['Released'],"Runtime":data['Runtime'].split(" ")[0],"Genre":data['Genre'],"Country":data['Country'],"Awards":data['Awards'],"BoxOffice":data['BoxOffice'],'imdbRating':data['imdbRating'],'Metascore':data['Metascore']}
                    else:
                        pass
            else:
                print(f"the search title was {data}. the correct title was {title}")
                print("Movie not found")
        
        file_path = 'output.json'
        with open(file_path, 'w') as json_file:
            json.dump(return_dict, json_file, indent=4)
        
        json_file.close()    
        return return_dict

rapid_api_data = create_rapid_api_json("21159c5c23msha7c9e5999b522ebp1fc04djsn9fb077c81d02", cur)


# create tables for genre, movie rating (pg-13, r, etc), and country (USA, UK, etc)
# Inputs: json data as a dictionary, database cursor object, database connection object
# Outputs: None

# explanation: set_up_types_tables takes a json dictionary, database cursor object, and database connection object and creates
# three tables: Genres, Rated, and MovieCountries in the database. The function first creates the Genres table. 
# It then loops through the json dictionary and adds each genre to a list. The function then loops through the list and adds
# each genre to the Genres table. The function then repeats this process for the Rated and MovieCountries tables.
# The function commits the changes to the database and returns None.
# No duplicate values are added to the tables and each value in each table recieves an ID number.
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
    pass

set_up_types_tables(rapid_api_data, cur, conn)

# Inputs: json data as a dictionary, database cursor object, database connection object
# Outputs: None (but prints out the number of added values to the database)
# Explanation: add_rapidapi_data_to_database adds the movie information from the json dictionary to the database. It first creates a 
# table called Rapid_API. It then loops through the json dictionary and checks if the movie title is in the dictionary.
# If the movie title is in the dictionary, the function checks if the movie title is in the database. If the movie title
# is not in the database, the function adds the movie title, id, year, rating, released, runtime, genre, country, awards, box office, IMDB rating, and metascore to the database.
# The function then commits the changes to the database and returns None. It prints out the number of added items. 
def add_rapidapi_data_to_database(movie_dict, conn, cur):
    added_count = 0
    cur.execute("CREATE TABLE IF NOT EXISTS Rapid_API (id INTEGER PRIMARY KEY, rated TEXT, released TEXT, runtime INTEGER, genre TEXT, country TEXT, awards TEXT, boxoffice TEXT, imdbRating INTEGER, metascore INTEGER)")
    cur.execute("SELECT MAX(id) FROM Rapid_API")
    last_id = cur.fetchone()[0]
    last_id = 0 if last_id is None else last_id

    for title in movie_dict.keys():
        if "imdbID" in movie_dict[title].keys() and "Rated" in movie_dict[title].keys() and "Released" in movie_dict[title].keys() and "Runtime" in movie_dict[title].keys() and "Genre" in movie_dict[title].keys() and "Country" in movie_dict[title].keys() and "Awards" in movie_dict[title].keys() and "BoxOffice" in movie_dict[title].keys() and "imdbRating" in movie_dict[title].keys() and "Metascore" in movie_dict[title].keys():
            cur.execute("SELECT COUNT(*) FROM Rapid_API WHERE id=?", (title,))
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
                try:
                    cur.execute("INSERT INTO Rapid_API (id, rated, released, runtime, genre, country, awards, boxoffice,imdbRating,metascore) VALUES (?,?,?,?,?,?,?,?,?,?)", (title, rating, movie_dict[title]['Released'], movie_dict[title]['Runtime'], genre, country, movie_dict[title]['Awards'], movie_dict[title]['BoxOffice'],movie_dict[title]['imdbRating'],movie_dict[title]['Metascore']))
                    added_count += 1
                except:
                    KeyError
                    pass
            

        if added_count == 25:
            break

    conn.commit()
    print(added_count)
    return None

add_rapidapi_data_to_database(rapid_api_data, conn, cur)
    
    