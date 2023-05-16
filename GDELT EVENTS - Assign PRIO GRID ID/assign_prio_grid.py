import getpass
import os
import configparser
import urllib.parse

from sqlalchemy import create_engine
import pandas as pd


# set up the connection to the database
SQL_HOST = "hpcc-sql.wharton.upenn.edu"
SQL_DB = "GDELT"
SQL_USER = getpass.getuser()
config = configparser.ConfigParser()
config.read(f"{os.environ['HOME']}/.my.cnf")
SQL_PASS = config["client"]["password"]


# fix up pass if it needs fixing for SQL Alchemy URL

SQL_PASS = urllib.parse.quote_plus(SQL_PASS)


# create a connection to the DB server

engine = create_engine(
    f"mariadb+pymysql://{SQL_USER}:{SQL_PASS}@{SQL_HOST}/{SQL_DB}?charset=utf8mb4"
)

sql = "SELECT ActionGeo_Lat, ActionGeo_Long FROM gdelt_events where Year = 2011 LIMIT 1000;"

df = pd.read_sql(sql, engine)
#print(df.head())

gid = pd.read_csv("PRIO GRID spine.csv")
#print(gid.head())

#Round of the coordinates in the GDELT EVENTS data to .25, .50, .75, .00 (that's how it is in PRIO GRID Spine)
pg_lat = []
pg_long = []

def lat_long_to_PG_lat_long(x,list_lat_long):
	for i in range(len(x)):
		if x[i] >= 0:
			if x[i] % 1 >= 0 and x[i] % 1 <= 0.5:
				list_lat_long.append(int(x[i]) + 0.25)
			else:
				list_lat_long.append(int(x[i]) + 0.75)

		if x[i] < 0:
			if x[i] % 1 >= 0 and x[i] % 1 <= 0.5:
				list_lat_long.append(int(x[i]) - 0.75)
			else:
				list_lat_long.append(int(x[i]) - 0.25)


lat_long_to_PG_lat_long(df["ActionGeo_Lat"],pg_lat)
lat_long_to_PG_lat_long(df["ActionGeo_Long"],pg_long)

df['pg_lat'] = pg_lat
df['pg_long'] = pg_long

#print(df)

a = df.merge(gid, how = "left", left_on = ["pg_lat","pg_long"], right_on = ["lat","lon"])
print(a)
