import mysql.connector
import pandas as pd

# Connect to the MySQL database on AWS RDS without specifying a database
mydb = mysql.connector.connect(
    host="sportswiki.c78k8gy42c1h.us-east-2.rds.amazonaws.com",
    port="3306",
    user="admin",
    password="cHKjaZwK9biQcaR9UM65"
)

# Create a new database if it doesn't exist
mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS sportswiki")

# Connect to the newly created database
mydb = mysql.connector.connect(
    host="sportswiki.c78k8gy42c1h.us-east-2.rds.amazonaws.com",
    port="3306",
    user="admin",
    password="cHKjaZwK9biQcaR9UM65",
    database="sportswiki"
)

mycursor = mydb.cursor()

print("Connected to the database successfully")

# Create tables with the specified attributes
mycursor.execute(
    '''CREATE TABLE IF NOT EXISTS Teams (
        Team varchar(64),
        ID int,
        Location varchar(64),
        Championships int,
        League varchar(64),
        Conference varchar(64),
        Founded int,
        Revenue int,
        Colors varchar(64),
        Attendance int,
        Ticket float,
        Stadium varchar(64),
        PRIMARY KEY (ID)
    )'''
)
data = pd.read_csv('teamsTable.csv',index_col= False)
sql = "INSERT INTO Teams (Team,ID,Championships,League,Conference,Founded,Revenue,Colors,Attendance,Ticket,Stadium) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
for i, row in data.iterrows():
    data_tuple = (
        row['Team'],
        row['ID'],
        row['Championships'],  # This assumes the typo in your example ('Championshsips') is fixed
        row['League'],
        row['Conference'],
        row['Founded'],
        row['Revenue'],
        row['Colors'],
        row['Attendance'],
        row['Ticket'],
        row['Stadium']
    )
    mycursor.execute(sql, data_tuple)
    mydb.commit()
'''
mycursor.execute(
    CREATE TABLE IF NOT EXISTS Staff (
        teamID INT,
        staffID INT AUTO_INCREMENT PRIMARY KEY,
        role VARCHAR(255),
        description TEXT,
        name VARCHAR(255),
        FOREIGN KEY (teamID) REFERENCES Teams(ID)
    )
)

mycursor.execute(
    CREATE TABLE IF NOT EXISTS Users (
        userID INT AUTO_INCREMENT PRIMARY KEY,
        admin BOOLEAN,
        username VARCHAR(255),
        password VARCHAR(255)
    )
)

mycursor.execute(
    CREATE TABLE IF NOT EXISTS Stadiums (
        name VARCHAR(255) PRIMARY KEY,
        capacity INT,
        address VARCHAR(255),
        ticket VARCHAR(255),
        attendance INT,
        location VARCHAR(255)
    )
)
'''

# Commit changes to the database
mydb.commit()

# Show databases (optional)
mycursor.execute("SHOW DATABASES")
