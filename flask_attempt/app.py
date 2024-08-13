from flask import Flask, render_template, url_for, request, redirect, session
import os
import pandas as pd
import requests
import db_connector as db

db_connection = db.connect_to_database()

training_sessions =[]

matches = []

datafile = None

app = Flask(__name__)
app.secret_key = 'hello'

@app.route('/')
def root():
    global db_connection
    db_connection = db.connect_to_database()
    query = "SHOW tables;"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
    if len(results) < 1:
        with open('DDL.sql', 'r') as file:
            sql_commands = file.read()
        commands = sql_commands.split(';')
        for command in commands:
            if command.strip():
                db.execute_query(db_connection=db_connection, query=command)

    query = "SELECT * FROM TrainingSessions"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    sessionResults = cursor.fetchall()
    print(sessionResults)
    query = "SELECT sessionID, COUNT(*) as count FROM Matches GROUP BY sessionID"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    matchResults = cursor.fetchall()
    return render_template("training_sessions.j2", sessionResults=sessionResults, matchResults=matchResults)

@app.route('/add_session', methods=['GET', 'POST'])
def add_session():
    if request.method == 'POST':
        sessionDate = request.form.get('date')
        gym = request.form.get('gym')
        focus = request.form.get('focus')
        query = f"INSERT INTO TrainingSessions(sessionDate, gym, focus)VALUES('{sessionDate}', '{gym}', '{focus}')"
        cursor = db.execute_query(db_connection=db_connection, query=query)
        return redirect(url_for('root'))
    else:
        return render_template('add_session.j2')

@app.route('/session_details/<int:id>')
def session_details(id):
    query = f"SELECT * FROM TrainingSessions where sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    sessionResults = cursor.fetchall()
    query = f"SELECT matchID, opponent, sessionID FROM Matches where sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    matchResults = cursor.fetchall()
    return render_template('session_details.j2', sessionResults=sessionResults, matchResults=matchResults)

@app.route('/update_session/<int:id>', methods=['GET', 'POST'])
def update_session(id):
    if request.method == 'POST':
        sessionDate = request.form.get('date')
        gym = request.form.get('gym')
        focus = request.form.get('focus')
        query = f"UPDATE TrainingSessions SET sessionDate='{sessionDate}', gym='{gym}', focus='{focus}' WHERE sessionID={id}"
        cursor = db.execute_query(db_connection=db_connection, query=query)
        return redirect(url_for('root'))
    else:
        query = f"SELECT * FROM TrainingSessions where sessionID={id}"
        cursor = db.execute_query(db_connection=db_connection, query=query)
        sessionResults = cursor.fetchall()
        query = f"SELECT matchID, opponent, sessionID FROM Matches where sessionID={id}"
        cursor = db.execute_query(db_connection=db_connection, query=query)
        matchResults = cursor.fetchall()
        return render_template('update_session.j2', sessionResults=sessionResults, matchResults=matchResults)

@app.route('/delete_session/<int:id>')
def delete_session(id):
    query = f"DELETE FROM TrainingSessions WHERE sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return redirect(url_for('root'))

@app.route('/you_sure/<int:id>')
def you_sure(id):
    return render_template('you_sure.j2', id=id)

@app.route('/delete_match/<int:match_id>')
def delete_match(match_id):
    query = f"SELECT sessionID FROM Matches WHERE matchID={match_id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    match = cursor.fetchall()
    match, = match
    query = f"DELETE FROM Matches WHERE matchID={match_id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return redirect(url_for('update_session', id=match["sessionID"]))

@app.route('/add_match/<int:id><int:count>', methods=['GET', 'POST'])
def add_match(id, count):
    if request.method == 'POST':
        opponent = request.form.get('opponent')
        matchMinutes = int(request.form.get('matchMinutes'))
        matchSeconds = int(request.form.get('matchSeconds'))
        focus = request.form.get('focus')
        notes = request.form.get('notes')
        matchHours = 0
        while matchMinutes >= 60:
            matchHours += 1
            matchMinutes -= 60
        if matchHours < 10:
            matchHours = "0"+str(matchHours)
        else:
            matchHours = str(matchHours)
        if matchMinutes < 10:
            matchMinutes = "0"+str(matchMinutes)
        else:
            matchMinutes = str(matchMinutes)
        if matchSeconds < 10:
            matchSeconds = "0"+str(matchSeconds)
        else:
            matchSeconds = str(matchSeconds)
        query = f"INSERT INTO Matches(opponent, duration, focus, notes, sessionID)VALUES('{opponent}', '{matchHours}:{matchMinutes}:{matchSeconds}', '{focus}', '{notes}', {id})"
        cursors = db.execute_query(db_connection=db_connection, query=query)
        if count != -1:
            count -= 1
        if count == -1 or count == 0:
            return redirect(url_for('update_session', id=id))
        else:
            return render_template('add_match_special.j2', match_session=id, count=count)
    else:
        if count == -1:
            return render_template('add_match.j2', match_session=id)
        else:
            return render_template('add_match_special.j2', match_session=id, count=count)


@app.route('/add_bulk_match/<int:id>', methods=['GET', 'POST'])
def add_bulk_match(id):
    if request.method == 'POST':
        count = request.form.get('bulk_num')
        return redirect(url_for('add_match', id=id, count=count))
    else:
        return render_template('add_bulk_matches.j2', session=id)

@app.route('/update_match/<int:match_id>', methods=['GET', 'POST'])
def update_match(match_id):
    if request.method == 'POST':
        opponent = request.form.get('opponent')
        matchMinutes = int(request.form.get('matchMinutes'))
        matchSeconds = int(request.form.get('matchSeconds'))
        focus = request.form.get('focus')
        notes = request.form.get('notes')
        matchHours = 0
        while matchMinutes >= 60:
            matchHours += 1
            matchMinutes -= 60
        if matchHours < 10:
            matchHours = "0"+str(matchHours)
        else:
            matchHours = str(matchHours)
        if matchMinutes < 10:
            matchMinutes = "0"+str(matchMinutes)
        else:
            matchMinutes = str(matchMinutes)
        if matchSeconds < 10:
            matchSeconds = "0"+str(matchSeconds)
        else:
            matchSeconds = str(matchSeconds)
        query = f"UPDATE Matches SET opponent='{opponent}', duration='{matchHours}:{matchMinutes}:{matchSeconds}', focus='{focus}', notes='{notes}' WHERE matchID={match_id}"
        cursors = db.execute_query(db_connection=db_connection, query=query)
        query = f"SELECT sessionID FROM Matches WHERE matchID={match_id}"
        cursors = db.execute_query(db_connection=db_connection, query=query)
        sessionID = cursors.fetchall()
        sessionID, = sessionID
        return redirect(url_for('update_session', id=sessionID['sessionID']))
        # 0:00:00
    else:
        query = f"SELECT * from Matches WHERE matchID={match_id}"
        cursor = db.execute_query(db_connection=db_connection,query=query)
        results = cursor.fetchall()
        results, = results
        duration = str(results['duration'])
        matchHours = int(duration[0])
        matchMinutes = int(duration[2:4])
        matchSeconds = int(duration[5:7])
        matchMinutes += matchHours * 60
        return render_template('update_match.j2', match=results, matchMinutes=matchMinutes, matchSeconds=matchSeconds)

@app.route('/match_details/<int:matchID>')
def match_details(matchID):
    query = f"SELECT * FROM Matches WHERE matchID={matchID}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
    results, = results
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
        query = f"INSERT INTO TrainingSessions(sessionDate, gym, focus)VALUES('{date}', '{gym}', '{focus}')"
        db.execute_query(db_connection=db_connection, query=query)
    
    session.pop('csv_data', None)
    session.pop('header_names', None)
    session.pop('file', None)
    
    return redirect(url_for('root'))



    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))


    app.run(port=port, debug=True)
