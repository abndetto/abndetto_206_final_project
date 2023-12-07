import sqlite3
import os
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

# connect to database
database_name = "Practice_DB"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + "/" + database_name)
cur = conn.cursor()


# get data from Rotten Tomatoes table in database
# only takes values of movies with a rating of 90 or higher
def get_rotten_tomatoes_data_score_over_90(cur):
    return_list = []
    cur.execute('SELECT title, id, year FROM Rotten_Tomatoes WHERE score >= 90')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2])
        return_list.append(rx)

    return return_list

# get all data from rapid api table in database
def get_rapid_api_data(cur):
    return_list = []
    cur.execute('SELECT title, id, year, rated, released, runtime, genre, country, awards, boxoffice,imdbRating,metascore FROM Rapid_API')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2], rval[3], rval[4], rval[5], rval[6], rval[7], rval[8], rval[9], rval[10], rval[11])
        return_list.append(rx)
        
    return return_list

# craete rapid api dataframe
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

# create rotten tomatoes dataframe 
rt_data = get_rotten_tomatoes_data_score_over_90(cur)

# add titles to dataframe and print

def rt_movies_by_year(rt_data):
    rt_titles = [movie[0] for movie in rt_data]
    rt_years = [movie[2] for movie in rt_data]
    rt_data = {'Title': rt_titles, 'Year': rt_years}
    rt_df = pd.DataFrame(rt_data)
    return_series = rt_df.groupby('Year').size().reset_index(name='Number of Movies')
    return return_series

# Plotting Rotten Tomato Data (number of movies that recieved 90+ score by year)
rt_movies_over_90_by_year = rt_movies_by_year(rt_data)
plt.figure(figsize=(10, 6))
plt.bar(rt_movies_over_90_by_year['Year'], rt_movies_over_90_by_year['Number of Movies'], color='skyblue')
plt.xlabel('Year')
plt.ylabel('Number of Movies')
plt.title('Number of Movies by Year With Rotten Tomatoes Score 90 or Higher')
plt.grid(axis='y')
plt.show()

def get_measurements_and_genres(cur):
    return_list = []
    cur.execute('SELECT Rapid_API.title, Rapid_API.metascore, Rapid_API.year, Genres.genre FROM Rapid_API JOIN Genres ON Rapid_API.genre = Genres.id')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2], rval[3])
        return_list.append(rx)

    genres_genre = [movie[3] for movie in return_list]
    genres_metascore = [movie[1] for movie in return_list]
    genre_data = {'Genre': genres_genre, 'Metascore': genres_metascore}
    gg_df = pd.DataFrame(genre_data)
    gg_df['Metascore'] = pd.to_numeric(gg_df['Metascore'], errors='coerce')
    gg_df = gg_df.dropna(subset=['Metascore'])
    avg_metascore_by_genre = gg_df.groupby('Genre').mean()
    return avg_metascore_by_genre

def get_measurements_and_countries(cur):
    return_list = []
    cur.execute('SELECT Rapid_API.title, Rapid_API.metascore, Rapid_API.year, MovieCountries.country FROM Rapid_API JOIN MovieCountries ON Rapid_API.country = MovieCountries.id')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2], rval[3])
        return_list.append(rx)
        
    countries_country = [movie[3] for movie in return_list]
    country_metascore = [movie[1] for movie in return_list]
    country_data = {'Country': countries_country, 'Metascore': country_metascore}
    cc_df = pd.DataFrame(country_data)
    cc_df['Metascore'] = pd.to_numeric(cc_df['Metascore'], errors='coerce')
    cc_df = cc_df.dropna(subset=['Metascore'])
    avg_metascore_by_country = cc_df.groupby('Country').mean()
    return avg_metascore_by_country




# with open('calculated_data_text.txt', 'w') as file:
x = get_measurements_and_countries(cur)
y = get_measurements_and_genres(cur)
rt_data = get_rotten_tomatoes_data_score_over_90(cur)
z = rt_movies_by_year(rt_data)
x = x.to_string()
y = y.to_string()
z = z.to_string()


with open('calculationsText.txt', 'w') as file:
    file.write("Calculated the average metascore by movie country of origin")
    file.write('\n')
    file.write(x)
    file.write('\n')
    file.write("Calculated the average metascore by movie genre")
    file.write('\n')
    file.write(y)
    file.write('\n')
    file.write("Calculated the number of recommended movies with a RT score equal to or higher than 90 by year")
    file.write('\n')
    file.write(z)
    file.close()
    
