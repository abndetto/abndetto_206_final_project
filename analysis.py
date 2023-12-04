import sqlite3
import os
import pandas as pd 
import matplotlib.pyplot as plt

# connect to database
database_name = "Practice_DB"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + "/" + database_name)
cur = conn.cursor()


# get data from Rotten Tomatoes table in database
def get_rotten_tomatoes_data_score_over_90(cur):
    return_list = []
    cur.execute('SELECT title, id, year FROM Rotten_Tomatoes WHERE score >= 90')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2])
        return_list.append(rx)

    return return_list

# get data from rapid api
def get_rapid_api_data(cur):
    return_list = []
    cur.execute('SELECT title, id, year, rated, released, runtime, genre, country, awards, boxoffice,imdbRating,metascore FROM Rapid_API')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2], rval[3], rval[4], rval[5], rval[6], rval[7], rval[8], rval[9], rval[10], rval[11])
        return_list.append(rx)
        
    return return_list


rapi_data = get_rapid_api_data(cur)
rapi_titles = [movie[1] for movie in rapi_data]
rapi_years = [movie[2] for movie in rapi_data]
rapi_rated = [movie[3] for movie in rapi_data]
rapi_released = [movie[4] for movie in rapi_data]
rapi_runtime = [movie[5] for movie in rapi_data]
rapi_genre = [movie[6] for movie in rapi_data]
rapi_country = [movie[7] for movie in rapi_data]
rapi_awards = [movie[8] for movie in rapi_data]
rapi_boxoffice = [movie[9] for movie in rapi_data]
rapi_imdbRating = [movie[10] for movie in rapi_data]
rapi_metascore = [movie[11] for movie in rapi_data]

rapi_data = {'Title': rapi_titles, 'Year': rapi_years, 'Rated': rapi_rated, 'Released': rapi_released, 'Runtime': rapi_runtime, 'Genre': rapi_genre, 'Country': rapi_country, 'Awards': rapi_awards, 'Box Office': rapi_boxoffice, 'IMDB Rating': rapi_imdbRating, 'Metascore': rapi_metascore}
rapi_df = pd.DataFrame(rapi_data)

print(rapi_df)


# print data pulled from database
rt_data = get_rotten_tomatoes_data_score_over_90(cur)

# add titles to dataframe and print
rt_titles = [movie[0] for movie in rt_data]
rt_years = [movie[2] for movie in rt_data]
rt_data = {'Title': rt_titles, 'Year': rt_years}
rt_df = pd.DataFrame(rt_data)

rt_movies_by_year = rt_df.groupby('Year').size().reset_index(name='Number of Movies')

# Plotting Rotten Tomato Data
# plt.figure(figsize=(10, 6))
# plt.bar(rt_movies_by_year['Year'], rt_movies_by_year['Number of Movies'], color='skyblue')
# plt.xlabel('Year')
# plt.ylabel('Number of Movies')
# plt.title('Number of Movies by Year With Rotten Tomatoes Score 90 or Higher')
# plt.grid(axis='y')
# plt.show()

