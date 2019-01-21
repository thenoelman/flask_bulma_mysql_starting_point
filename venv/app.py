from flask import Flask, render_template, session, request, flash, url_for, redirect
from flaskext.mysql import MySQL
import pymysql, json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "9tUPxDo8F8qDzZ7Ogwhg"

mysql = MySQL()

# config mysql
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'unjobbed'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def index():
    logged_in = is_logged_in()
    return render_template('index.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    logged_in = is_logged_in()
    if request.method == 'POST':
        error = None
        print('i am in here')
        email = request.form['emailaddress']
        pwd = request.form['pword']
        print(pwd)
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM unjobbed_access WHERE email = %s", (email))
            row = cursor.fetchone()

            if row:
                pw = row["password"]
                pwCheck = check_password_hash(pw, pwd)
                if (pwCheck):
                    flash('You have successfully logged in.')

                    session['logged_in']= True
                    session['email'] = email

                    logged_in = is_logged_in()
                    
                    return redirect(url_for('dashboard'), logged_in=logged_in)
                else:
                    error = 'Log in error'
                    flash('Log in error')
                    return render_template('login.html', error=error, logged_in=logged_in)                   

            else:
                error = 'Log in error'
                flash('Log in error')
                return render_template('login.html', error=error, logged_in=logged_in)

        except Exception as e:
            error = 'Log in error'
            flash('Log in error')
            print(e)
        finally:
                conn.close()
    else:
        return render_template('login.html', error=error, logged_in=logged_in)    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    logged_in = is_logged_in()
    if request.method == 'POST':
        email = request.form['emailaddress']
        pwd = request.form['pword']
        cpwd = request.form['confpword']
        _hashed_password = generate_password_hash(pwd)

        if (pwd != cpwd):
            error = 'Your passwords do not match'
            flash('Your passwords do not match')
        else:
            #check to see if the user exists already
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM unjobbed_access where email = %s", (email))
            unj = cursor.fetchall()

            if unj:
                error = 'Email address is already registered'
                flash('Email address is already registered.  Please log in.')
                return render_template('login.html', error=error, logged_in=logged_in) 
            else:
                #create the login
                sql = "INSERT INTO unjobbed_access (email,password,forgot_login,admin_login) VALUES (%s, %s, %s, %s)"
                data = (email, _hashed_password, 0, 0)
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                return render_template('dashboard.html', error=error, logged_in=logged_in)
    else:
        return render_template('signup.html', error=error, logged_in=logged_in)   

@app.route('/dashboard')
def dashboard():

    logged_in = is_logged_in()

    if logged_in:
        return render_template('dashboard.html', logged_in=logged_in)        
    else:
        error = 'You are not logged in.'
        flash('You are not logged in.')
        return render_template('login.html', error=error)

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')   

@app.route('/profile')
def profile():
    logged_in = is_logged_in()

    return render_template('profile.html', logged_in=logged_in)    

@app.route('/logout')
def logout():
    session.clear()
    flash('You are logged out')
    return redirect(url_for('login')) 

def is_logged_in():
    if session.get('email') is None:
        return False
    return True    

if __name__== '__main__':
    app.secret_key='9tUPxDo8F8qDzZ7Ogwhg'
    app.run(debug=True)