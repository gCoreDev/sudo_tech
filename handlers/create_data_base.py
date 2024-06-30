import sqlite3

conn_tests = sqlite3.connect('data/data_base/tests.db')
conn_users = sqlite3.connect('data/data_base/users.db')
conn_results = sqlite3.connect('data/data_base/results.db')
conn_answers = sqlite3.connect('data/data_base/answers.db')
conn_messages = sqlite3.connect('data/data_base/messages.db')
cur_tests = conn_tests.cursor()
cur_users = conn_users.cursor()
cur_results = conn_results.cursor()
cur_answers = conn_answers.cursor()
cur_messages = conn_messages.cursor()


cur_users.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        user_full_name TEXT,
        user_username TEXT,
        user_type TEXT	
    )
''')
conn_users.commit()


cur_tests.execute('''
    CREATE TABLE IF NOT EXISTS tests 
    (
        id INTEGER PRIMARY KEY,
        name TEXT,
        questions TEXT,
        created_at TEXT
    )
''')
conn_tests.commit()


cur_messages.execute('''
    CREATE TABLE IF NOT EXISTS messages
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_type TEXT,
        message TEXT,
        reply_to INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )   
''')
conn_messages.commit()


cur_results.execute('''
    CREATE TABLE IF NOT EXISTS results
    (
        id INTEGER PRIMARY KEY,
        test_id INTEGER,
        test_name TEXT,
        full_name TEXT,
        answer TEXT,
        answer_text TEXT,
        created_at TEXT
    )
''')
conn_results.commit()


