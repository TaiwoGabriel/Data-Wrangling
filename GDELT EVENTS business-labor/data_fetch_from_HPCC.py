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

sql = f"SELECT * FROM gdelt_events where Year = 1990 and (Actor1Code LIKE 'BUS' OR Actor1Code LIKE 'MNC') and Actor2Code LIKE 'LAB';"
bus_lab = pd.read_sql(sql,engine)

sql = f"SELECT * FROM gdelt_events where Year = 1990 and (Actor2Code LIKE 'BUS' OR Actor2Code LIKE 'MNC') and Actor1Code LIKE 'LAB';"
lab_bus = pd.read_sql(sql,engine)

for i in range(1991,2022):
	print(i)

	sql = f"SELECT * FROM gdelt_events where Year = {i} and (Actor1Code LIKE 'BUS' OR Actor1Code LIKE 'MNC') and Actor2Code LIKE 'LAB';"
	bus_lab = pd.concat([bus_lab, pd.read_sql(sql,engine)]) 

	sql = f"SELECT * FROM gdelt_events where Year = {i} and (Actor2Code LIKE 'BUS' OR Actor2Code LIKE 'MNC') and Actor1Code LIKE 'LAB';"
	lab_bus = pd.concat([lab_bus, pd.read_sql(sql,engine)]) 		

print(bus_lab)
bus_lab.to_csv("bus_lab.csv",index=False)

print(lab_bus)
lab_bus.to_csv("lab_bus.csv",index=False)
