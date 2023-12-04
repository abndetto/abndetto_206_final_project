import requests 
import time
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
def get_rotten_tomatoes_data(cur):
    return_list = []
    cur.execute('SELECT title, id, year FROM  Rotten_Tomatoes')
    for rval in cur:
        rx = (rval[0], rval[1], rval[2])
        return_list.append(rx)

    return return_list

# print data pulled from database
rt_data = get_rotten_tomatoes_data(cur)

# add titles to dataframe and print
rt_titles = [movie[0] for movie in rt_data]
rt_years = [movie[2] for movie in rt_data]
rt_data = {'Title': rt_titles, 'Year': rt_years}
df = pd.DataFrame(rt_data)

rt_movies_by_year = df.groupby('Year').size().reset_index(name='Number of Movies')

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(rt_movies_by_year['Year'], rt_movies_by_year['Number of Movies'], color='skyblue')
plt.xlabel('Year')
plt.ylabel('Number of Movies')
plt.title('Number of Movies by Year')
plt.grid(axis='y')
plt.show()

