import mysql.connector

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
        ID INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        championships INT,
        league VARCHAR(255),
        conference VARCHAR(255),
        revenue FLOAT,
        colors VARCHAR(255),
        founded DATE,
        stadium VARCHAR(255)
    )'''
)

mycursor.execute(
    '''CREATE TABLE IF NOT EXISTS Staff (
        teamID INT,
        staffID INT AUTO_INCREMENT PRIMARY KEY,
        role VARCHAR(255),
        description TEXT,
        name VARCHAR(255),
        FOREIGN KEY (teamID) REFERENCES Teams(ID)
    )'''
)

mycursor.execute(
    '''CREATE TABLE IF NOT EXISTS Users (
        userID INT AUTO_INCREMENT PRIMARY KEY,
        admin BOOLEAN,
        username VARCHAR(255),
        password VARCHAR(255)
    )'''
)

mycursor.execute(
    '''CREATE TABLE IF NOT EXISTS Stadiums (
        name VARCHAR(255) PRIMARY KEY,
        capacity INT,
        address VARCHAR(255),
        ticket VARCHAR(255),
        attendance INT,
        location VARCHAR(255)
    )'''
)
# Define the user details
user_data = {
    "admin": False,  # Set to True if the user is an admin, False otherwise
    "username": "example_user",
    "password": "example_password"
}

# Insert the user into the Users table
sql = "INSERT INTO Users (admin, username, password) VALUES (%s, %s, %s)"
val = (user_data["admin"], user_data["username"], user_data["password"])

mycursor.execute(sql, val)
# Commit changes to the database
mydb.commit()
# Execute a SELECT query to retrieve all rows from the Users table
mycursor.execute("SELECT * FROM Users")

# Fetch all rows from the result set
users = mycursor.fetchall()

# Print the retrieved user data
for user in users:
    print(user)
# Show databases (optional)
mycursor.execute("SHOW DATABASES")
