from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/FYEO')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

info_log = db.infos

app = Flask(__name__, static_url_path='')

@app.route('/')
def infos_main():
    """Return homepage."""
    return render_template('infos_main.html', infos=info_log.find())

@app.route('/infos/new')
def infos_new():
    """Return to the new adoption profile page"""
    return render_template('infos_new.html', info={}, title='New Account Info Log')

@app.route('/infos', methods=['POST'])
def infos_submit():
    """Submit a new adoption profile. Allows the user to input information for the adoption ad."""
    info = {
        'img_url': request.form.get('img_url'),
        'name': request.form.get('name'),
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }
    print(info)
    info_id = info_log.insert_one(info).inserted_id
    return redirect(url_for('infos_main', info_id=info_id))

@app.route('/infos/<info_id>')
def infos_show(info_id):
    """Show a single account info log"""
    info = info_log.find_one({'_id': ObjectId(info_id)})
    return render_template('infos_show.html', info=info)

@app.route('/infos/<info_id>/edit')
def infos_edit(info_id):
    """Show the edit form for an account info log."""
    info = info_log.find_one({'_id': ObjectId(info_id)})
    return render_template('infos_edit.html', info=info, title='Edit Account Info')

@app.route('/infos/<info_id>', methods=['POST'])
def infos_update(info_id):
    """Submit an edited log."""
    updated_info = {
        'img_url': request.form.get('img_url'),
        'name': request.form.get('name'),
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }
    info_log.update_one(
        {'_id': ObjectId(info_id)},
        {'$set': updated_info})
    return redirect(url_for('infos_show', info_id=info_id))

@app.route('/infos/<info_id>/delete', methods=['POST'])
def infos_delete(info_id):
    """Delete one account info log."""
    info_log.delete_one({'_id': ObjectId(info_id)})
    return redirect(url_for('infos_main'))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))