from flask import Flask, render_template, request, redirect
import psycopg2
import os
import time

app = Flask(__name__)

def get_db():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'db'),
                database=os.environ.get('DB_NAME', 'tododb'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres')
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print("Database not ready, waiting 3 seconds...")
            time.sleep(3)
    raise Exception("Could not connect to database!")

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO todos (task) VALUES (%s)', (task,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM todos WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
