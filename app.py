from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hdfbefuiehreuhfekjfheihueh' #anything complex
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'

db = SQLAlchemy(app)


class UserAccount(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(35), unique=True)
    fullname = db.Column(db.String(25))
    password = db.Column(db.String(50))


class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70))
    author = db.Column(db.String(25))
    genre = db.Column(db.String(20))
    amazon_url = db.Column(db.String(300))
    user_id = db.Column(db.ForeignKey(UserAccount.account_id))


def verify_token(token_param):
    @wraps(token_param)
    def decorators_func(*args, **kwargs):
        token = None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
        if not token:
            return jsonify({'message': 'Token not found!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            logged_user = UserAccount.query.filter_by(account_id=data['account_id']).first()
        except:
            return jsonify({'message': 'Your session has expired, login again.'})
        return token_param(logged_user, *args, **kwargs)
    return decorators_func


@app.route('/register', methods=['POST'])
def create_user():
    account_details = request.get_json()
    hashed_password = generate_password_hash(account_details['password'], method='sha256')
    new_user = UserAccount(email=account_details['email'], fullname=account_details['fullname'],
                           password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New User created'})


@app.route('/login')
def login():
    authorize = request.authorization

    if not authorize or not authorize.username or not authorize.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm "Login Required"'})
    user = UserAccount.query.filter_by(email=authorize.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm "You are not registered."'})
    if check_password_hash(user.password, authorize.password):
        token = jwt.encode({'account_id': user.account_id, 'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=45)},
                           app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm "Incorrect Password"'})


@app.route('/library', methods=['GET'])
@verify_token
def list_all_books(logged_user):
    books = Library.query.filter_by(user_id=logged_user.account_id).all()
    booklist = []
    for book in books:
        book_details = {}
        book_details['id'] = book.id
        book_details['title'] = book.title
        book_details['author'] = book.author
        book_details['genre'] = book.genre
        book_details['amazon_url'] = book.amazon_url
        booklist.append(book_details)
    return jsonify({'Books': booklist})


@app.route('/library/<book_id>', methods=['GET'])
@verify_token
def retrieve_one_book(logged_user, book_id):
    book = Library.query.filter_by(id=book_id, user_id=logged_user.account_id).first()
    if not book:
        return jsonify({'message': 'No book found'})
    book_details = {}
    book_details['id'] = book.id
    book_details['title'] = book.title
    book_details['author'] = book.author
    book_details['genre'] = book.genre
    book_details['amazon_url'] = book.amazon_url
    return jsonify({'Book': book_details})


@app.route('/library', methods=['POST'])
@verify_token
def add_book(logged_user):
    data = request.get_json()
    new_book = Library(title=data['title'], author=data['author'], genre=data['genre'], amazon_url=data['amazon_url'],
                       user_id=logged_user.account_id)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book Saved!'})


@app.route('/library/<book_id>', methods=['PUT'])
@verify_token
def update_book_details(logged_user, book_id):
    book = Library.query.filter_by(id=book_id, user_id=logged_user.account_id).first()
    if not book:
        return jsonify({'message': 'No book found'})
    data = request.get_json()
    book.title = data['title']
    book.author = data['author']
    book.genre = data['genre']
    book.amazon_url = data['amazon_url']
    db.session.commit()
    return jsonify({'message': 'Book Updated!'})


@app.route('/library/<book_id>', methods=['DELETE'])
@verify_token
def delete_book(logged_user, book_id):
    book = Library.query.filter_by(id=book_id, user_id=logged_user.account_id).first()
    if not book:
        return jsonify({'message': 'No book found'})
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book Deleted!'})


if __name__ == '__main__':
    app.run(debug=True)

