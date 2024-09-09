from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

# Function to connect to the database
def connect_db():
    conn = mysql.connector.connect(
        host='db',
        user='root',
        password='26102003',
        database='waka'
    )
    return conn

# Function to generate access token
def generate_access_token(identity):
    return create_access_token(identity=identity)

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    phone_number = data['phone_number']
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM reader WHERE phone_number = %s", (phone_number,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'message': 'Phone number already exists'}), 400
        else:
            cursor.execute("INSERT INTO reader (username, password, phone_number) VALUES (%s, %s, %s)", (username, password, phone_number))
            conn.commit()
            return jsonify({'message': 'Registration successful'}), 200
    except Error as e:
        return jsonify({'message': 'Registration failed', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM reader WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            access_token = generate_access_token(identity=user['reader_id'])
            return jsonify({'message': 'Login successful', 'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    except Error as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Protected endpoint
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Logout endpoint
@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    return jsonify({'message': 'Successfully logged out'}), 200

# Favorite a book endpoint
@app.route('/favorite/<int:book_id>', methods=['POST'])
@jwt_required()
def add_to_favorites(book_id):
    current_user = get_jwt_identity()
    reader_id = current_user
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM favorite WHERE reader_id = %s AND book_id = %s", (reader_id, book_id))
        existing_favorite = cursor.fetchone()
        if existing_favorite:
            return jsonify({'message': 'Book is already in favorites'}), 400
        else:
            cursor.execute("INSERT INTO favorite (reader_id, book_id) VALUES (%s, %s)", (reader_id, book_id))
            conn.commit()
            return jsonify({'message': 'Book added to favorites'}), 200
    except Error as e:
        return jsonify({'message': 'Failed to add book to favorites', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()


# Unfavorite a book endpoint
@app.route('/unfavorite/<int:book_id>', methods=['DELETE'])
@jwt_required()
def remove_from_favorites(book_id):
    current_user = get_jwt_identity()
    reader_id = current_user
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM favorite WHERE reader_id = %s AND book_id = %s", (reader_id, book_id))
        existing_favorite = cursor.fetchone()
        if not existing_favorite:
            return jsonify({'message': 'Book is not in favorites'}), 400
        else:
            cursor.execute("DELETE FROM favorite WHERE reader_id = %s AND book_id = %s", (reader_id, book_id))
            conn.commit()
            return jsonify({'message': 'Book removed from favorites'}), 200
    except Error as e:
        return jsonify({'message': 'Failed to remove book from favorites', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Get books by category endpoint for logged-in users
@app.route('/books/<category>', methods=['GET'])
@jwt_required(optional=True)
def get_books_by_category(category):
    current_user = get_jwt_identity()
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if current_user:
            cursor.execute("SELECT book.book_id, title, thumb, author_id, author_name, CASE WHEN favorite_id IS NULL THEN FALSE ELSE TRUE END AS is_favorite FROM book LEFT JOIN (SELECT book_id, favorite_id FROM favorite WHERE reader_id = %s) AS fav ON book.book_id = fav.book_id WHERE category = %s", (current_user, category))
        else:
            cursor.execute("SELECT book_id, title, thumb, author_id, author_name, FALSE AS is_favorite FROM book WHERE category = %s", (category,))
        
        books = cursor.fetchall()
        return jsonify(books), 200
    except Error as e:
        return jsonify({'message': 'Failed to fetch books', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Get books by category endpoint for guests
@app.route('/guest/books/<category>', methods=['GET'])
def get_books_by_category_guest(category):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT book_id, title, thumb, author_id, author_name, FALSE AS is_favorite FROM book WHERE category = %s", (category,))
        books = cursor.fetchall()
        return jsonify(books), 200
    except Error as e:
        return jsonify({'message': 'Failed to fetch books', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Search endpoint
@app.route('/search/<search_key>', methods=['GET'])
def search(search_key):
    if not search_key:
        return jsonify({'message': 'Search key is required'}), 400
    
    search_key = search_key.lower()

    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT title, author_name FROM book WHERE LOWER(title) LIKE %s OR LOWER(author_name) LIKE %s", ('%' + search_key + '%', '%' + search_key + '%'))
        search_results = cursor.fetchall()
        return jsonify(search_results), 200
    except Error as e:
        return jsonify({'message': 'Failed to search books', 'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# insert table book
@app.route('/insert_book/<category>', methods=['POST'])
def insert_book(category):
    if request.is_json:
        data = request.get_json()
        book_id = data.get('book_id')
        title = data.get('title')
        thumb = data.get('thumb')
        author_id = data.get('author_id')
        author_name = data.get('author_name')
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO book (book_id, title, category, thumb, author_id, author_name) VALUES (%s, %s, %s, %s, %s, %s)",
                           (book_id, title, category, thumb, author_id, author_name))
            conn.commit()
            return jsonify({'message': 'Book inserted successfully'}), 200
        except Error as e:
            return jsonify({'message': 'Failed to insert book', 'error': str(e)}), 400
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'message': 'Request must be JSON'}), 400





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
