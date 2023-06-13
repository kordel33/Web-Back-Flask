from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

# Utwórz instancję aplikacji Flask
app = Flask(__name__)
app.secret_key = "mysecretkey"

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

# Model danych
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(50))
    is_available = db.Column(db.Boolean)

class BorrowedBooks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer)

# Definiuje ścieżki i funkcje obsługujące żądania HTTP
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']

            # Sprawdzanie, czy nazwa użytkownika już istnieje
            existing_user = User.query.filter_by(name=name).first()
            if existing_user:
                flash('Nazwa użytkownika jest już zajęta.')
                return redirect(url_for('add_user'))
            else:
                user = User(name=name, password=password)
                db.session.add(user)
                db.session.commit()
                flash('Pomyślnie utworzono użytkownika')
                return redirect(url_for('add_user'))         
        else:
            return render_template('add_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(name=username, password=password).first()

        if user:
            session['username'] = username
            return redirect(url_for('biblioteka'))
        else:
            flash('Błędny login lub hasło. Spróbuj ponownie.')
            return redirect(url_for('login'))
    else:
        return render_template('index.html')
    
# Wylogowanie
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Po zalogowaniu
@app.route('/biblioteka')
def biblioteka():
    books = Books.query.all()
    borrowed = BorrowedBooks.query.all()
    return render_template('biblioteka.html', books=books, borrowed=borrowed)

# Tworzenie bazy danych
@app.route('/createdb')
def create_db():
    db.create_all()
    return "Utworzono bazę danych"

# Wypozyczenie
@app.route('/borrow', methods=['POST'])
def borrow():
    pole1 = request.form['pole1']
    pole2 = request.form['pole2']

    # Sprawdzenie, czy książka jest już wypożyczona
    wypozyczona_ksiazka = BorrowedBooks.query.filter_by(book_id=pole1).first()
    if wypozyczona_ksiazka:
        flash('Ta książka jest już wypożyczona.')
        return redirect(url_for('biblioteka'))

    dane = BorrowedBooks(book_id=pole1, user_id=pole2)
    db.session.add(dane)
    db.session.commit()
    flash('Dane zostały zapisane.')

    dane2 = Books.query.get(pole1)
    if dane2:
        dane2.is_available = False
        db.session.commit()
    return redirect(url_for('biblioteka'))

# Zwrocenie
@app.route('/refund', methods=['POST'])
def refund():
    pole1 = request.form['pole1']
    pole2 = request.form['pole2']

    # Sprawdzenie, czy książka zostala wypozyczona
    wypozyczona_ksiazka = BorrowedBooks.query.filter_by(book_id=pole1).first()
    if not wypozyczona_ksiazka:
        flash('Ta książka nie zostala wypozyczona')
        return redirect(url_for('biblioteka'))

    dane = BorrowedBooks.query.filter_by(book_id=pole1, user_id=pole2).first()
    if dane:
        db.session.delete(dane)
        db.session.commit()
    flash('Dane zostały zapisane.')
    
    dane2 = Books.query.get(pole1)
    if dane2:
        dane2.is_available = True
        db.session.commit()
    return redirect(url_for('biblioteka'))

# Uruchom serwer
if __name__ == '__main__':
    app.run(port=8081, debug=True)