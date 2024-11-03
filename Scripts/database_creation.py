import sqlite3
import pandas as pd
# Connect to sqlite
connection=sqlite3.connect("placements.db")

#Create a cursor 
cursor=connection.cursor()

#create placements table
table_info="""
Create table STUDENT(
    ROLL_NUMBER INT NOT NULL,
    STUDENT_NAME VARCHAR(25),
    COMPANY_PLACED VARCHAR(30),
    COMPENSATION_OFFERED FLOAT
);
"""
cursor.execute(table_info)

# #insert values into database from csv
df=pd.read_csv("cse_stats.csv")
df.to_sql("STUDENT", connection, if_exists='append', index=False)

#print all records
data=cursor.execute(""" SELECT * FROM STUDENT""")
for row in data:
    print(row)

#Close the connection
connection.commit()
connection.close()