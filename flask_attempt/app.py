from flask import Flask, render_template, url_for, request, redirect, session
import os
import pandas as pd
import requests
import db_connector as db

db_connection = db.connect_to_database()

datafile = None

app = Flask(__name__)
app.secret_key = 'hello'

@app.route('/')
def root():
    requests.get("http://127.0.0.1:9113/create-db")
    results = requests.get("http://127.0.0.1:9113/display-sessions")
    results = results.json()
    sessionResults = results[0]
    matchResults = results[1]
    return render_template("training_sessions.j2", sessionResults=sessionResults, matchResults=matchResults)

@app.route('/add_session', methods=['GET', 'POST'])
def add_session():
    if request.method == 'POST':
        response = requests.post("http://127.0.0.1:9114/insert-session", data=request.form)
        print(response)
        return redirect(url_for('root'))
    else:
        return render_template('add_session.j2')

@app.route('/session_details/<int:id>')
def session_details(id):
    results = requests.get(f"http://127.0.0.1:9113/display-session/{id}")
    results = results.json()
    sessionResults = results[0]
    print(sessionResults)
    matchResults = results[1]
    return render_template('session_details.j2', sessionResults=sessionResults, matchResults=matchResults)

@app.route('/update_session/<int:id>', methods=['GET', 'POST'])
def update_session(id):
    if request.method == 'POST':
        response = requests.post(f"http://127.0.0.1:9114/update-session/{id}", data=request.form)
        return redirect(url_for('root'))
    else:
        results = requests.get(f"http://127.0.0.1:9113/display-session/{id}")
        results = results.json()
        sessionResults = results[0]
        matchResults = results[1]
        return render_template('update_session.j2', sessionResults=sessionResults, matchResults=matchResults)

@app.route('/delete_session/<int:id>')
def delete_session(id):
    response = requests.post(f"http://127.0.0.1:9115/delete-session", data={'delete':id})
    return redirect(url_for('root'))

@app.route('/you_sure/<int:id>')
def you_sure(id):
    return render_template('you_sure.j2', id=id)

@app.route('/delete_match/<int:match_id>')
def delete_match(match_id):
    response = requests.post(f"http://127.0.0.1:9115/delete-match", data={'match_id':match_id})
    match = response.json()
    print(match)
    return redirect(url_for('update_session', id=match[0]["sessionID"]))

@app.route('/add_match/<int:id>', methods=['GET', 'POST'])
def add_match(id):
    if request.method == 'POST':
        response = requests.post(f"http://127.0.0.1:9114/insert-match/{id}", data=request.form)
        return redirect(url_for('update_session', id=id))
    else:
        return render_template('add_match.j2', match_session=id)

@app.route('/add_multiple_matches/<int:id>/<int:count>', methods=['GET', 'POST'])
def add_multiple_matches(id, count):
    if request.method == 'POST':
        response = requests.post(f"http://127.0.0.1:9114/insert-match/{id}", data=request.form)
        count -= 1
        if count == 0:
            return redirect(url_for('update_session', id=id))
        else:
            return render_template('add_match_special.j2', match_session=id, count=count)
    else:
        return render_template('add_match_special.j2', match_session=id, count=count)

@app.route('/add_bulk_match/<int:id>', methods=['GET', 'POST'])
def add_bulk_match(id):
    if request.method == 'POST':
        count = request.form.get('bulk_num')
        return redirect(url_for('add_multiple_matches', id=id, count=count))
    else:
        return render_template('add_bulk_matches.j2', session=id)

@app.route('/update_match/<int:match_id>', methods=['GET', 'POST'])
def update_match(match_id):
    if request.method == 'POST':
        response = requests.post(f"http://127.0.0.1:9114/update-match/{match_id}", data=request.form)
        response = response.json()
        print(response)
        return redirect(url_for('update_session', id=response[0]['sessionID']))
    else:
        results = requests.get(f"http://127.0.0.1:9113/display-match/{match_id}")
        results = results.json()
        results = results[0]
        duration = str(results['duration'])
        matchHours = int(duration[0:2])
        matchMinutes = int(duration[3:5])
        matchSeconds = int(duration[6:8])
        matchMinutes += matchHours * 60
        return render_template('update_match.j2', match=results, matchMinutes=matchMinutes, matchSeconds=matchSeconds)

@app.route('/match_details/<int:matchID>')
def match_details(matchID):
    results = requests.get(f"http://127.0.0.1:9113/display-match/{matchID}")
    results = results.json()
    results = results[0]
    return render_template('match_details.j2', results=results)

@app.route('/step1_display', methods=['GET'])
def step1_display():
    file = session.get('file', '')
    return render_template('step1.j2', file=file)

@app.route('/step1', methods=['POST'])
def step1():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    session['file'] = file.filename
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.csv'):
        datafile = pd.read_csv(file)
        data_list = datafile.to_dict(orient='records')
        session['csv_data'] = data_list
        
        return redirect(url_for('step2'))
    
    return redirect(request.url)

@app.route('/step2', methods=['GET', 'POST'])
def step2():
    header_names = session.get('header_names', [])
    if request.method == 'POST':
        session.pop('header_names', None)
        header_names = []
        header_names.append(request.form['date'])
        header_names.append(request.form['gym'])
        header_names.append(request.form['focus'])
        session['header_names'] = header_names
        return redirect(url_for('step3'))
    return render_template('step2.j2', header_names=header_names)

@app.route('/step3', methods=['GET'])
def step3():
    if 'header_names' not in session:
        return redirect(url_for('step2'))
    headers = session.get('header_names')
    filename = session.get('file')
    return render_template('step3.j2', headers=headers, filename=filename)

@app.route('/step4', methods=['POST'])
def step4():
    if 'csv_data' not in session:
        return redirect(url_for('step1'))
    
    data_list = session['csv_data']
    header_names = session['header_names']
    
    for data in data_list:
        date = data[header_names[0]]
        adjusted_date = ''
        for character in date:
            if character == '/':
                adjusted_date += '-'
            else:
                adjusted_date += character
        response = requests.get(f"https://first-test-4sfy.onrender.com/date-converter/{adjusted_date}")
        response = response.json()
        date = response['date-converted']
        gym = data[header_names[1]]
        focus = data[header_names[2]]
        response = requests.post("http://127.0.0.1:9114/insert-session", data={'date':date, 'gym':gym, 'focus':focus})
    
    session.pop('csv_data', None)
    session.pop('header_names', None)
    session.pop('file', None)
    
    return redirect(url_for('root'))



    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))
    app.run(port=port, debug=True)
