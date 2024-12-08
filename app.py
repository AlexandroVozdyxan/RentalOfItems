from flask import Flask, render_template, redirect
from flask import request
import sqlite3
app = Flask(__name__)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Db_open_close(object):
    def __init__(self, database):
        self.con = sqlite3.connect('db1.db')
        self.con.row_factory = dict_factory
        self.cur = self.con.cursor()
    def __enter__(self):
        return self.cur
    def __exit__(self, type, value, traceback):
        self.con.commit()
        self.con.close()
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        return 'POST'
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO user
            (login, password, ipn, full_name, contacts, photo, passport)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (form_data['login'], form_data['password'], form_data['ipn'], form_data['full_name'],
                           form_data['contacts'], form_data['photo'], form_data['passport']
                           ))

        return redirect('/login')

@app.route('/logout', methods=['GET', 'POST', 'DELETE'])
def logout():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def profile():
    if request.method == 'GET':
        return render_template('user.html')
    if request.method == 'PUT':
        return 'PUT'
    if request.method == 'PATCH':
        return 'PATCH'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/favorites', methods=['GET', 'POST', 'DELETE'])
def favorites():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/favorites/<favorites_id>', methods=['GET', 'PUT', 'DELETE'])
def favorites_id(favorites_id):
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/profile/search_history', methods=['GET', 'DELETE'])
def search_history():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'DELETE':
        return 'DELETE'

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        with Db_open_close('db1.db') as db_cur:
            db_cur.execute("SELECT * FROM item")
            items = db_cur.fetchall()
        return render_template('items.html', items=items)
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            db_cur.execute('''INSERT INTO item (photo, name, description, price_hour, price_day, price_week, price_month, owner)
            VALUES (:photo, :name, :description, :price_hour, :price_day, :price_week, :price_month, :owner)''', request.form)
        return redirect('/items')

@app.route('/items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
def item(item_id):
    if request.method == 'GET':
        return render_template('oneitemform.html', item_id=item_id)
    if request.method == 'PUT':
        return f'PUT {item_id}'
    if request.method == 'DELETE':
        return f'DELETE {item_id}'

@app.route('/leasers', methods=['GET'])
def leasers():
    if request.method == 'GET':
        return 'GET'

@app.route('/leasers/<leaser_id>', methods=['GET'])
def leaser(leaser_id):
    if request.method == 'GET':
        return f'GET: {leaser_id}'

@app.route('/contracts', methods=['GET', 'POST'])
def contracts():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/contracts/<contract_id>', methods=['GET', 'PUT', 'PATCH'])
def contracts_id(contract_id):
    if request.method == 'GET':
        return f'GET: {contract_id}'
    if request.method == 'PUT':
        return f'PUT: {contract_id}'
    if request.method == 'PATCH':
        return f'PATCH: {contract_id}'

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'POST':
        return 'POST'

@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if request.method == 'GET':
        return render_template('feedback.html')
    if request.method == 'POST':
        with Db_open_close('db1.db') as db_cur:
            form_data = request.form
            db_cur.execute('''INSERT INTO feedback
            (author, user, text, grade, contract)
            VALUES (?, ?, ?, ?, ?)''',
            (form_data['author'], form_data['user'],
             form_data['text'], form_data['grade'],
             form_data['contract'])
                           )
        return render_template('complain_sub.html')

@app.route('/complaints/<complaint_id>', methods=['GET', 'PUT', 'DELETE'])
def complaints_id(complaint_id):
    if request.method == 'GET':
        return f'GET: {complaint_id}'
    if request.method == 'PUT':
        return f'PUT: {complaint_id}'
    if request.method == 'DELETE':
        return f'DELETE: {complaint_id}'

@app.route('/compare', methods=['GET', 'PUT'])
def compare():
    if request.method == 'GET':
        return 'GET'
    if request.method == 'PUT':
        return 'PUT'

if __name__ == '__main__':
    app.run()
