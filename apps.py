from flask import Flask, render_template, request , redirect, url_for, session, jsonify
import mysql.connector
import hashlib
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import mpld3
import numpy as np
matplotlib.use('Agg') #needed for graph to work
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' 


mydb = mysql.connector.connect(
            host="sportswiki.c78k8gy42c1h.us-east-2.rds.amazonaws.com",
            port="3306",
            user="admin",
            password="cHKjaZwK9biQcaR9UM65",
            database="sportswiki"
        )

class UserAuthenticator:
    def __init__(self):
        
        self.cursor = mydb.cursor()

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
        mydb.commit()
        return True  # Registration was successful
        

    def login(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM Users WHERE username = %s AND password = %s", (username, hashed_password))
        user = self.cursor.fetchone()
        if user:
            session['is_admin'] = user[1]  # Store admin status in session
            return True  # If user is not None, login successful
        else:
            return False

    def deactivate_account(self, username):
        self.cursor.execute("DELETE FROM Users WHERE username = %s", (username,))
        mydb.commit()
        return self.cursor.rowcount > 0  # Returns True if any row was deleted, meaning account was found and deleted

authenticator = UserAuthenticator()
class Teams:        #function to get filtered teams calling db
    def __init__(self):
        self.cursor = mydb.cursor()

    def filtered_teams(self, league, y_value, color=None, city=None, year=None, maxmin=None):
        sql = "Select t.* "

        if y_value == "owners":
            y_value = "Owners"
            sql += ", (SELECT COUNT(*) FROM Staff WHERE Tid = t.ID AND Position = 'Owner') AS Owners FROM Teams t"
            if city:
                sql += " left join Stadiums s on t.Stadium = s.Name"
        elif y_value == "stadium-capacity" or city:
            if (y_value == "stadium-capacity"):
                y_value = "stadium_capacity"
                sql += ",s.size As stadium_capacity"
            sql += " From Teams t left join Stadiums s on t.Stadium = s.Name"
        else:
            sql += " From Teams t"
        
        sql += " WHERE 1=1"
        params = []
        if league != "All":
            sql += " And t.League = %s"
            params.append(league)
        if color:
            sql += " AND t.Colors LIKE %s"
            params.append('%' + color + '%')
        if city:
            sql += " AND s.location LIKE %s" 
            params.append(f'%{city},%') 
        if year:
            sql += " AND t.Founded = %s"
            params.append(year)
        if maxmin == "+":
            sql += " ORDER BY " + y_value + " DESC"
        else:
            sql += " ORDER BY " + y_value + " ASC"

        print(params)
        self.cursor.execute(sql, params)
        result = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        df = pd.DataFrame(result, columns=column_names)

        

        return df,y_value.capitalize()
    

    
teamcommand = Teams()


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
        return redirect(url_for('home'))
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

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/results')
def results():
    term = request.args.get('term')
    if term:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Teams WHERE Team LIKE %s", ('%' + term + '%',))
        teams = cursor.fetchall()
        print("Teams:", teams)
        return render_template('results.html', teams=teams)
    else:
        return "No search term provided"
    
@app.route('/team/<int:team_id>')
def team_details(team_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Teams WHERE id = %s", (team_id,))
    team = cursor.fetchone()
    cursor.execute("SELECT * FROM Staff WHERE Tid = %s", (team_id,))
    staff = cursor.fetchall()
    cursor.close()
    for staff_member in staff:
        if staff_member['Sid'] == 0:
            staff_member['Role'] = 'Owner'
        elif staff_member['Sid'] == 1:
            staff_member['Role'] = 'Head Coach'
    
    if team:
        return render_template('team_details.html', team=team, staff=staff, is_admin=session.get('is_admin', False))
    else:
        return "Team not found"

@app.route('/comparePage')  #takes to compare page
def compare():
    return render_template('compare.html')

@app.route('/compareFilters', methods=['POST']) #compare features
def filters():
    #get mandatory filters
    league = request.form.get('league')
    y_value = request.form.get('y-value')
    if not league:
        league=="All"
    if not y_value:
        return "Please select a y-value"
    #optional filters
    color = request.form.get('color')
    city = request.form.get('city')
    year = request.form.get('year')
    maxmin = request.form.get('max-min')
    filteredteams, yvalue = teamcommand.filtered_teams(league, y_value, color, city, year, maxmin)
    #make sure the filtered teams are not empty and shrink if too large
    if len(filteredteams) == 0:
        return "No teams found with the given filters"
    elif len(filteredteams) > 10:
        filteredteams = filteredteams[:10]
    html_table = filteredteams.to_html(index=False)
    plt.figure(figsize=(10,6))
    bars = plt.bar(filteredteams['Team'], filteredteams[yvalue], width = 0.5)
    plt.ylabel(yvalue)
    plt.title('Filtered Teams vs '+yvalue)
    plt.gca().set_xticklabels(filteredteams['Team'])
    plt.tight_layout()
    plot_html = mpld3.fig_to_html(plt.gcf())
    
    return (render_template('graph.html', html_table = html_table, plot_html=plot_html))

@app.route('/save_changes', methods=['POST'])
def save_changes():
    cursor = mydb.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json  # Get the JSON data from the request
        team_id = data.get('teamID')
        team_name = data.get('teamName')
        championships = data.get('championships')
        league = data.get('league')
        conference = data.get('conference')
        revenue = data.get('revenue')
        colors = data.get('colors')
        founded = data.get('founded')
        stadium = data.get('stadium')
        staff_data = data.get('staff')
        tickets = data.get('ticket')
        attendance = data.get('attendance')
        
        # Update team details
        update_team_query = '''
            UPDATE Teams 
            SET Team = %s, championships = %s, league = %s, conference = %s, 
                revenue = %s, colors = %s, founded = %s, stadium = %s, ticket = %s, attendance = %s
            WHERE ID = %s
        '''
        team_values = (team_name, championships, league, conference, revenue, colors, founded, stadium, tickets, attendance, team_id)
       
        cursor.execute(update_team_query, team_values)

        
        # Update staff details
        for staff_member in staff_data:
            update_staff_query = '''
                UPDATE Staff 
                SET Name = %s, position = %s, description = %s 
                WHERE Sid = %s
            '''
            staff_values = (staff_member.get('name'), staff_member.get('position'), staff_member.get('description'), staff_member.get('staffID'))
            
            cursor.execute("SELECT Sid FROM Staff WHERE Sid = %s", (staff_member.get('staffID'),))
            sid_from_db = cursor.fetchone()

            cursor.execute(update_staff_query, staff_values)

        
        mydb.commit()  # Commit the changes to the database
         # Re-fetch the updated data from the database
        cursor.execute("SELECT * FROM Teams WHERE ID = %s", (team_id,))
        updated_team = cursor.fetchone()
        cursor.execute("SELECT * FROM Staff WHERE Tid = %s", (team_id,))
        updated_staff = cursor.fetchall()
        
        cursor.close()
        
        # Render the template with the updated data
        return render_template('team_details.html', team=updated_team, staff=updated_staff, is_admin=session.get('is_admin', False))
    else:
        return jsonify({'message': 'Invalid request method.'}), 405

if __name__ == '__main__':
    app.run(debug=True)
    
