from flask import Flask, render_template, url_for, request, redirect, session
import os
import pandas as pd

training_sessions =[]

matches = []

datafile = None

app = Flask(__name__)
app.secret_key = 'hello'

@app.route('/')
def root():
    print(training_sessions)
    print(matches)
    return render_template("training_sessions.j2", people=training_sessions, matches=matches)

@app.route('/add_session')
def add_session():
    return render_template('add_session.j2')

@app.route('/save_session', methods=['POST'])
def save_session():
    global training_sessions
    if len(training_sessions) != 0:
        new_session = {
            "id": training_sessions[-1]["id"] + 1,
            "date": request.form['date'],
            'gym': request.form['gym'],
            'focus': request.form['focus']
        }
    else:
        new_session = {
            "id": 0,
            "date": request.form['date'],
            'gym': request.form['gym'],
            'focus': request.form['focus']
        }
    training_sessions.append(new_session)
    return redirect(url_for('root'))

@app.route('/update_session/<int:id>', methods=['POST'])
def save_update_session(id):
    global training_sessions
    update_session = None
    for item in training_sessions:
        if item['id'] == id:
            update_session = item
    new_data = {
        "id": id,
        "date": request.form['date'],
        'gym': request.form['gym'],
        'focus': request.form['focus'],
    }
    update_session.update(new_data)
    return redirect(url_for('root'))

@app.route('/session_details/<int:id>')
def session_details(id):
    session = None
    for item in training_sessions:
        if item['id'] == id:
            session = item
    associated_matches = []
    for match in matches:
        if match["session_id"] == id:
            associated_matches.append(match)
    return render_template('session_details.j2', session=session, associated_matches=associated_matches)

@app.route('/update_session/<int:id>')
def update_session(id):
    session = None
    for item in training_sessions:
        if item['id'] == id:
            session = item
            break
    associated_matches = []
    for match in matches:
        if match["session_id"] == id:
            associated_matches.append(match)
    return render_template('update_session.j2', session=session, associated_matches=associated_matches)

@app.route('/delete_session/<int:id>')
def delete_session(id):
    global training_sessions
    global matches
    session = None
    for item in training_sessions:
        if item['id'] == id:
            session = item
    training_sessions.remove(session)
    for match_index in range(len(matches)):
        match = matches[match_index]
        if match['session_id'] == id:
            matches[match_index] = None
    matches = [item for item in matches if item != None]
    return redirect(url_for('root'))

@app.route('/you_sure/<int:id>')
def you_sure(id):
    session = None
    for item in training_sessions:
        if item['id'] == id:
            session = item
    return render_template('you_sure.j2', session=session)

@app.route('/delete_match/<int:id>/<int:match_id>')
def delete_match(id, match_id):
    global matches
    match = None
    for item in matches:
        if item["session_id"] == id and item["match_id"] == match_id:
            match = item
            matches.remove(match)
    return redirect(url_for('update_session', id=match["session_id"]))

@app.route('/add_match/<int:id>')
def add_match(id):
    match_session = None
    for session in training_sessions:
        if session['id'] == id:
            match_session = session
    return render_template('add_match.j2', match_session=match_session)


@app.route('/add_bulk_match/<int:id>')
def add_bulk_match(id):
    session = None
    for item in training_sessions:
        if item['id'] == id:
            session = item
    return render_template('add_bulk_matches.j2', session=session)

@app.route('/adding_matches/<int:id>', methods=['POST'])
def adding_matches(id):
    count = request.form['bulk_num']
    return redirect(url_for('add_match_special', id=id, count=count))

@app.route('/add_match_special/<int:id>/<int:count>')
def add_match_special(id, count):
    if count == 0:
        return redirect(url_for('update_session', id=id))
    match_session = None
    for session in training_sessions:
        if session['id'] == id:
            match_session = session
    return render_template('add_match_special.j2', match_session=match_session, count=count)

@app.route('/save_match_special/<int:id>/<int:count>', methods=['POST'])
def save_match_special(id, count):
    global matches
    if len(matches) != 0:
        new_match = {
            "session_id": id,
            "match_id": matches[-1]["match_id"] + 1,
            "opponent": request.form['opponent'],
            'duration': request.form['duration'],
            'focus': request.form['focus'],
            'notes': request.form['notes']
        }
    else:
        new_match = {
            "session_id": id,
            "match_id": 0,
            "opponent": request.form['opponent'],
            'duration': request.form['duration'],
            'focus': request.form['focus'],
            'notes': request.form['notes']
        }

    matches.append(new_match)
    # if count > 1:
    return redirect(url_for('add_match_special', id=id, count=count-1))
    # else:
        # return redirect(url_for('update_session', id=id))
    # return 

@app.route('/update_match/<int:id>/<int:match_id>')
def update_match(id, match_id):
    match = None
    for item in matches:
        if item["session_id"] == id and item["match_id"] == match_id:
            match = item
    return render_template('update_match.j2', match=match)

@app.route('/match_details/<int:id>/<int:match_id>')
def match_details(id, match_id):
    match = None
    for item in matches:
        if item["session_id"] == id and item["match_id"] == match_id:
            match = item
    return render_template('match_details.j2', match=match)

@app.route('/save_match/<int:id>', methods=['POST'])
def save_match(id):
    global matches
    if len(matches) != 0:
        new_match = {
            "session_id": id,
            "match_id": matches[-1]["match_id"] + 1,
            "opponent": request.form['opponent'],
            'duration': request.form['duration'],
            'focus': request.form['focus'],
            'notes': request.form['notes']
        }
    else:
        new_match = {
            "session_id": id,
            "match_id": 0,
            "opponent": request.form['opponent'],
            'duration': request.form['duration'],
            'focus': request.form['focus'],
            'notes': request.form['notes']
        }

    matches.append(new_match)
    return redirect(url_for('update_session', id=new_match['session_id']))

@app.route('/save_update_match/<int:id>/<int:match_id>', methods=['POST'])
def save_update_match(id, match_id):
    global matches
    update_match = None
    for item in matches:
        if item['session_id'] == id and item['match_id'] == match_id:
            update_match = item
    new_data = {
        "opponent": request.form['opponent'],
        'duration': request.form['duration'],
        'focus': request.form['focus'],
        'notes': request.form['notes']
    }
    update_match.update(new_data)
    return redirect(url_for('update_session', id=update_match["session_id"]))

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
    global training_sessions
    if 'csv_data' not in session:
        return redirect(url_for('step1'))
    
    data_list = session['csv_data']
    header_names = session['header_names']
    
    for data in data_list:
        new_session = {
            "id": training_sessions[-1]["id"] + 1 if training_sessions else 1,
            "date": data.get(header_names[0]),
            'gym': data.get(header_names[1]),
            'focus': data.get(header_names[2]),
        }
        training_sessions.append(new_session)
    
    session.pop('csv_data', None)
    session.pop('header_names', None)
    session.pop('file', None)
    
    return redirect(url_for('root'))



    

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))


    app.run(port=port, debug=True)
