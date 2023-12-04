import requests 
import time
import sqlite3
import os
import pandas as pd 

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

# Print the DataFrame
display(df)