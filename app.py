from flask import Flask, render_template, request, redirect, url_for,send_from_directory
import csv
import os
import bcrypt
app = Flask(__name__)

EVENTS_CSV = 'events.csv'
EVENTS_HEADER = ['EventName', 'Category', 'Date', 'Location', 'Description', 'ContactInfo', 'File']

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
        writer.writerow([username, hashed.decode('utf-8')])


# The correct logic relies on comparing the hashes using bcrypt:
USERS_CSV_HEADER = ['username', 'password']


# --- Helper Function: Get ALL user data ---
def get_all_users():
    """Reads the USERS_CSV and returns a dictionary: {username: password_hash}"""
    users = {}
    if os.path.exists(USERS_CSV):
        try:
            with open(USERS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                # Use fieldnames to ensure DictReader recognizes the lowercase headers
                reader = csv.DictReader(csvfile, fieldnames=USERS_CSV_HEADER)
                
                # Skip the header row if it exists (DictReader reads the first line)
                if os.stat(USERS_CSV).st_size > len(','.join(USERS_CSV_HEADER)):
                    next(reader) 
                    
                for row in reader:
                    # Access CSV data using lowercase keys 'username' and 'password'
                    users[row['username']] = row['password']
        except Exception as e:
            print(f"Error reading users CSV file: {e}") 
    return users

# --- Helper Function: Get a SINGLE user's data ---
def get_user_data(username):
    """
    Looks up a username and returns a dictionary of their credentials 
    if found, or None otherwise.
    """
    users = get_all_users()
    stored_hash_str = users.get(username)
    if stored_hash_str:
        # Returns dictionary using the lowercase 'password' key to match check_user logic
        return {'username': username, 'password': stored_hash_str}
    return None

# --- Helper Function: Check Password ---
def check_user(username, password):
    """Authenticates a user against the stored bcrypt hash."""
    user_data = get_user_data(username)
    
    if not user_data:
        return False # User not found

    # Uses the key 'password' from the dictionary returned by get_user_data
    stored_hash_str = user_data['password'] 
    
    # 1. Convert stored hash string back into a byte string
    stored_hash_bytes = stored_hash_str.encode('utf-8')
    
    # 2. Encode the plain text password input into bytes
    input_password_bytes = password.encode('utf-8')
    
    # 3. Compare the two byte strings using bcrypt.checkpw
    return bcrypt.checkpw(input_password_bytes, stored_hash_bytes)

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
        'Date': request.form.get('Time'),
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
    return send_from_directory('flyers',filename)


if __name__ == "__main__":
    app.run(debug=True)
