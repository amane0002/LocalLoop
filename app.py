from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = 'events.csv'
CSV_HEADER = ['EventName', 'Category', 'Date', 'Location', 'Description', 'ContactInfo','File']

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(CSV_HEADER)


@app.route('/')
def login():
    return render_template('log-in.html')

@app.route('/home', methods=['POST', 'GET'])
def home():
    return render_template('index.html')


@app.route('/addevent')
def add_event():
    return render_template('addevent.html')


@app.route('/submitEvent', methods=['POST'])
def submitEvent():
    event_data = {
        'EventName': request.form.get('EventName'),
        'Category': request.form.get('Category'),
        'Date': request.form.get('Date'),
        'Location': request.form.get('Location'),
        'Description': request.form.get('Description'),
        'ContactInfo': request.form.get('ContactInfo'),
        'File' : request.files.get('file'),   # 'file' is the name attribute of the <input>
    }
    file = event_data['File'] 
    file.save(os.path.join('flyers', file.filename))


    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
        writer.writerow(event_data)

    print(f"✅ Event added: {event_data['EventName']}")
    return redirect(url_for('display_events'))



@app.route('/events')
@app.route('/events/<category_name>')
def display_events(category_name='all'):
    events = []
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if category_name.lower() == "all" or row["Category"].lower() == category_name.lower():
                    events.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    return render_template('find.html', events=events)


if __name__ == '__main__':
    app.run(debug=True)


## User Log in ## Hashed Password Version Yay ##
CSV_FILE = 'users.csv'

def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Create CSV if it doesn't exist
    if not os.path.isfile(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username','password'])
    
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed.decode()])

def check_user(username, password):
    if not os.path.isfile(CSV_FILE):
        return False
    with open(CSV_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['username'] == username and bcrypt.checkpw(password.encode(), row['password'].encode()):
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def login_page():
    message = ""
    if request.method == 'POST':
        if request.form['action'] == 'login':
            username = request.form['username']
            password = request.form['password']
            if check_user(username, password):
                message = "Login successful!"
            else:
                message = "Invalid username or password."
        elif request.form['action'] == 'signup':
            username = request.form['username']
            password = request.form['password']
            add_user(username, password)
            message = "User registered! You can now log in."
    return render_template('login.html', message=message)

if __name__ == "__main__":
    app.run(debug=True)
