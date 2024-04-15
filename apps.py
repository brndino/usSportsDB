from flask import Flask, render_template, request , redirect, url_for
import hashlib

app = Flask(__name__)

class UserAuthenticator:
    def __init__(self):
        self.credentials = {}
        self.load_credentials()

    def load_credentials(self):
        try:
            with open('credentials.txt', 'r') as file:
                for line in file:
                    username, password = line.strip().split( ':' )
                    self.credentials[username] = password
        except FileNotFoundError:
            pass

    def save_credentials(self):
        with open('credentials.txt', 'w') as file:
            for username, password in self.credentials.items():
                file.write(f"{username}:{password}\n")

    def register(self, username, password):
        if username in self.credentials:
            return False  #The username already exist.
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.credentials[username] = hashed_password
        self.save_credentials()
        return True  # Registration was successful

    def login(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return username in self.credentials and self.credentials[username] == hashed_password

    def deactivate_account(self, username):
        if username in self.credentials:
            del self.credentials[username]
            self.save_credentials()
            return True  # The Account is Activated.
        else:
            return False  # The Account was not found within the system.

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
