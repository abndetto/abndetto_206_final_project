# to run the program, first initialize the database and the base data values by 
# running the rotten tomatoes file (RTdata.py) 6 times. This will add the necessary 
# movie titles to the database in increments of 25. Next, run the rapidAPI.py file 6 times to pass the rotten tomato 
# movie titles through the rapid api. This program will save the data to a json file so it will only 
# need to call the api twice for each movie dictionary. The data is stored in output.json. The database will be populated 
# by the output.json file data. Finally, run the analysis.py file to pull data from the database,
# transform it into dataframes, and use for visualization and analysis.