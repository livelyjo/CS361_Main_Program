from flask import Flask, request
import os
import db_connector as db

app = Flask(__name__)

@app.route('/insert-session', methods=['POST'])
def insert_session():
    db_connection = db.connect_to_database()
    sessionDate = request.form.get('date')
    gym = request.form.get('gym')
    focus = request.form.get('focus')
    query = f"INSERT INTO TrainingSessions(sessionDate, gym, focus)VALUES('{sessionDate}', '{gym}', '{focus}')"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return '200'

@app.route('/insert-match/<int:id>', methods=['POST'])
def insert_match(id):
    db_connection = db.connect_to_database()
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
    return '200'

@app.route('/update-session/<int:id>', methods=['POST'])
def update_session(id):
    db_connection = db.connect_to_database()
    sessionDate = request.form.get('date')
    gym = request.form.get('gym')
    focus = request.form.get('focus')
    query = f"UPDATE TrainingSessions SET sessionDate='{sessionDate}', gym='{gym}', focus='{focus}' WHERE sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return '200'

@ app.route('/update-match/<int:match_id>', methods=['POST'])
def update_match(match_id):
    db_connection = db.connect_to_database()
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
    return [sessionID]



if __name__=="__main__":
    port = int(os.environ.get('PORT', 9114))
    app.run(port=port, debug=True)