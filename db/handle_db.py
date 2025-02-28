import sqlite3

def init_db():
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()


def insert_user(username, password):
    # Ensure username and password are strings
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError("Username and password must be strings")
    
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password) VALUES (?, ?)
        ''', (username, password))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_user(username):
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE username = ?
    ''', (username,))
    user = cursor.fetchone()

    conn.close()
    return user

def retrieve_password(username):
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT password FROM users WHERE username = ?
    ''', (username,))
    password = cursor.fetchone()

    conn.close()
    
    if password is None:
        return None
    return password
    

def main():
    init_db()

    #example code
    insert_user('admin', 'admin')
    print(get_user('admin'))
    print(retrieve_password('admin'))


if __name__ == '__main__':
    main()







