from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Expense_Logger')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

info_log = db.info
users = db.users
current_User = db.current_user

app = Flask(__name__)

@app.route('/')
def index():
    """return homepage"""
    return render_template('index.html', infos=info_log.find())

@app.route('/delete/account')
def delete_an_account():
    '''Render a page to delete account'''
    current = ""
    for document in current_User.find():
        current = document['username']
    # Render a page to redirect account
    return render_template('delete.html', current_username=current)

@app.route('/delete_user', methods = ['POST'])
def delete_user():
    '''Delete a user from rubber ducky website'''
    current = ""
    for document in current_User.find():
        current = document['username']

    # If the html form's content of the name 'password' is None that
    # means the website should be rendered again
    if request.form.get('password') is None:
        return render_template('delete.html', current_username=current)
        
    # Search the current user
    collection = users.find({ 'username': current})
    for document in collection:
        # If the password entered is correct, delete the current user's account
        if document['password'] == request.form.get('password'):
            users.delete_one({'username':current})
            # Resets current user to blank and redirects to index
            user = {
                'username':'',
                'password':''
            }
            current_User.update_one({'username':current}, {'$set':user})
            return redirect(url_for('index'))
        # Otherwise pass a boolean argument notifying the user that they have entered an incorrect password
        return render_template('delete.html', incorrect_password=True, current_user=current)


@app.route('/sign_in_user', methods = ['POST'])
def sign_in_user():
    ''' Have an existing user sign back in '''
    current = ""
    for document in current_User.find():
        current = document['username']

    # See if the username the user entered in an html exists
    cursor = users.find({'username': request.form.get('username')})
    for document in cursor:
        # Compare their entered password to the password recorded in the database
        if document['password'] != request.form.get('password'):
            # Password entered by the user doesn't match, pass a boolean argument to let them know
            return render_template('login.html', current_username="", incorrect_password=True)
        # The passwords matched, update the current user info
        username = request.form.get('username')
        user = {
            'username':username
        }
        current_User.update_one({'username':current}, {'$set':user })
        return redirect(url_for("index"))
    # If the username entered doesn't match the records pass in a boolean argument to let the user know  
    return render_template('login.html', current_username="", username_does_not_exist=True)

@app.route('/user/leaving')
def user_leaving():
    ''' Render the main page without a user signed in '''
    current = ""
    for document in current_User.find():
        current = document['username']
    
    # Sign the current user off by setting the current user's values equal to empty strings
    user = {
            'username':'',
            'password':''
        }
    current_User.update_one({'username':current}, {'$set':user})

    return redirect(url_for('index'))

@app.route('/user/new')
def user_new():
    ''' Render a page to allow a new user to sign up '''
    current = ""
    for document in current_User.find():
        current = document['username']
    return render_template('signup.html', current_username=current)

@app.route('/save_user', methods=['POST'])
def register_user():
    ''' Create a new user given the previous specs '''
    current = ""
    for document in current_User.find():
        current = document['username']

    # Get query information
    cursor = users.find({ 'username': request.form.get('username')})

    # Return username is already taken if a document exists
    for document in cursor:
        return render_template('create_new_user.html', current_username=current, username_is_taken=True)

    # Returns no_passwords if a password was not entered
    if request.form.get('password') is "" or request.form.get('retype_password') is "":
        return render_template('create_new_user.html', current_username=current, no_password=True)

    # Return passwords_differ if a password mismatch exists
    if request.form.get('password') != request.form.get('retype_password'):
        return render_template('create_new_user.html', current_username=current, passwords_differ=True)

    # Create a user document based on the contents of the forms, include the cart_id above
    user_info = {
        'username' : request.form.get('username'),
        'password' : request.form.get('password')
    }
    users.insert_one(user_info)

    # Sign out the current user after a new account is created, by updating current user's values
    # to empty strings
    if current != "":
        user = {
            'username':'',
            'password':''
        }
        current_User.update_one({'username':current}, {'$set':user })
    return redirect(url_for('user_returning'))

@app.route('/user/returning')
def user_returning():
    ''' Render a page to allow an existing user to sign in'''
    current = ""
    for document in current_User.find():
        current = document['username']
    return render_template('login.html', current_username=current)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))