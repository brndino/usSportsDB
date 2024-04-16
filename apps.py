from flask import Flask, render_template, request , redirect, url_for
import mysql.connector
import hashlib

app = Flask(__name__)

class UserAuthenticator:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="sportswiki.c78k8gy42c1h.us-east-2.rds.amazonaws.com",
            port="3306",
            user="admin",
            password="cHKjaZwK9biQcaR9UM65",
            database="sportswiki"
        )
        self.cursor = self.db.cursor()

    def register(self, username, password):
        print(f"Received username: {username}, password: {password}")
    
        # Check if the username already exists
        self.cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
        user = self.cursor.fetchone()
        if user:
            return False  # The username already exists
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        sql = "INSERT INTO Users (admin, username, password) VALUES (%s, %s, %s)"
        val = (False, username, hashed_password)
        self.cursor.execute(sql, val)
        self.db.commit()
        return True  # Registration was successful
        

    def login(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, hashed_password))
        user = self.cursor.fetchone()
        return bool(user)  # If user is not None, login successful

    def deactivate_account(self, username):
        self.cursor.execute("DELETE FROM Users WHERE username = %s", (username,))
        self.db.commit()
        return self.cursor.rowcount > 0  # Returns True if any row was deleted, meaning account was found and deleted

authenticator = UserAuthenticator()

@app.route('/')
def index():
    return render_template('index.html', message = None)




@app.route('/registration', methods=[ 'POST' ]) #updates to the next page once registration was successful.
def register():
    username = request.form[ 'username' ]
    password = request.form[ 'password' ]
    if authenticator.register( username, password ):
        return render_template('index.html', message= "Registration is successful.")
    else:
        return render_template('index.html', message="This username already exists. Please choose another username please.")






@app.route('/login', methods=[ 'POST' ]) #updates to next page and shows that login was successful.
def login():
    username = request.form['username']
    password = request.form['password']
    if authenticator.login(username, password):
        return "Login Was Successful!"
    else:
        return "Invalid Username and/or Password."


@app.route('/loginPage') 
def login_page():
    return render_template('login.html')


@app.route('/deactivate', methods=[ 'POST'] ) #updates the next page when app is deactivated.
def deactivate():
    username = request.form[ 'username' ]
    if authenticator.deactivate_account(username):
        return "Account Was Removed From the System!"
    else:
        return "Account Is Invalid/Not Found"

if __name__ == '__main__':
    app.run(debug=True)
    
