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
mycursor.execute("""

        CREATE TABLE IF NOT EXISTS Teams (
    Team varchar(64),
    ID int,
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
    )
"""
)

#Name,Position,Desc,Tid,Sid
mycursor.execute('''
    CREATE TABLE IF NOT EXISTS Staff (
        Name VARCHAR(64),
        Tid INT,
        Sid INT PRIMARY KEY,
        Position VARCHAR(255),
        Description text,
        FOREIGN KEY (Tid) REFERENCES Teams(ID)
    )'''
)

mycursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        userID INT AUTO_INCREMENT PRIMARY KEY,
        admin BOOLEAN,
        username VARCHAR(255),
        password VARCHAR(255)
                
    )
                 '''
    
)
#Name,Size,Location
mycursor.execute('''
    CREATE TABLE IF NOT EXISTS Stadiums (
        name VARCHAR(255),
        size INT,
        Location VARCHAR(255),
        PRIMARY KEY (name)
    )'''
)


# Commit changes to the database
mydb.commit()

# Show databases (optional)
mycursor.execute("SHOW DATABASES")
