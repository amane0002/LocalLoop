from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import csv
import os
import bcrypt
app = Flask(__name__)

EVENTS_CSV = 'events.csv'
EVENTS_HEADER = ['EventName', 'Category','Time', 'Date', 'Location', 'Description', 'ContactInfo', 'File']

if not os.path.exists(EVENTS_CSV):
    with open(EVENTS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(EVENTS_HEADER)

USERS_CSV = 'users.csv'
if not os.path.exists(USERS_CSV):
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'password'])


def add_user(username, password):
    username = (username or "").strip()
    password = (password or "").strip()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed.decode()])


def check_user(username, password):
    # Authentication bypass: accept any credentials
    return True


def user_exists(username):
    username = (username or "").strip()
    with open(USERS_CSV, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('username', '').strip() == username:
                return True
    return False


@app.route('/', methods=['GET', 'POST'])
def login_page():
    """Main login/signup page"""
    message = ""
    if request.method == 'POST':
        action = request.form.get('action', '').strip()
        username = (request.form.get('username') or '').strip()
        password = (request.form.get('password') or '').strip()

        if action == 'login':
            if check_user(username, password):
                return redirect(url_for('flappy'))  # 🎮 Go to the Flappy game
            else:
                message = "Invalid username or password."

        elif action == 'signup':
            if not username or not password:
                message = "Please provide both username and password."
            elif user_exists(username):
                message = "Username already exists. Please log in."
            else:
                add_user(username, password)
                message = "User registered! You can now log in."

    return render_template('log-in.html', message=message)


@app.route('/home')
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
        'Time': request.form.get('Time'),
        'Date': request.form.get('Date'),
        'Location': request.form.get('Location'),
        'Description': request.form.get('Description'),
        'ContactInfo': request.form.get('ContactInfo'),
    }

    file = request.files.get('file')
    if file and file.filename != '':
        flyers_path = 'flyers'
        os.makedirs(flyers_path, exist_ok=True)
        file.save(os.path.join(flyers_path, file.filename))
        event_data['File'] = file.filename
    else:
        event_data['File'] = ''

    with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=EVENTS_HEADER)
        writer.writerow(event_data)

    print(f"✅ Event added: {event_data['EventName']}")
    return redirect(url_for('display_events'))


@app.route('/events')
@app.route('/events/<category_name>')
def display_events(category_name='all'):
    events = []
    try:
        with open(EVENTS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if category_name.lower() == "all" or row["Category"].lower() == category_name.lower():
                    events.append(row)
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    return render_template('find.html', events=events)


@app.route('/flappy')
def flappy():
    """Flappy Burghy Game Page"""
    return render_template('flappy.html')


@app.route('/flyers/<filename>')
def serve_flyer(filename):
    """
    Serves the event flyer image files securely from the 'flyers' directory.
    This route is called from the <img> tag in find.html.
    """
    # This securely serves the file from the UPLOAD_FOLDER (which is 'flyers')
    return send_from_directory('flyers', filename)


if __name__ == "__main__":
    app.run(debug=True)
