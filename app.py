from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = 'events.csv'
CSV_HEADER = ['EventName', 'Category', 'Date', 'Location', 'Description', 'ContactInfo']

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(CSV_HEADER)


@app.route('/')
def index():
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
    }

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
