import sqlite3
import pandas as pd
# Connect to sqlite
connection=sqlite3.connect("placements.db")

#Create a cursor 
cursor=connection.cursor()

#create placements table
student_table="""
Create table STUDENT(
    ROLL_NUMBER INT NOT NULL,
    STUDENT_NAME VARCHAR(25),
    COMPANY_PLACED VARCHAR(30),
    COMPENSATION_OFFERED FLOAT
);
"""
internship_offers_table="""
Create table INTERNSHIP_OFFERS(
    COMPANY VARCHAR(30),
    STIPEND_OFFERED FLOAT,
    STUDENTS_COUNT INT
);
"""
cursor.execute(student_table)
cursor.execute(internship_offers_table)

# #insert values into database from csv
df_placement_stats=pd.read_csv("Data/cse_stats.csv")
df_placement_stats.to_sql("STUDENT", connection, if_exists='append', index=False)

df_internship_stats=pd.read_csv("Data/internship_stats.csv")
df_internship_stats.to_sql("INTERNSHIP_OFFERS",connection,if_exists='append', index=False)

#print all records
data=cursor.execute(""" SELECT * FROM INTERNSHIP_OFFERS""")
for row in data:
    print(row)

#Close the connection
connection.commit()
connection.close()