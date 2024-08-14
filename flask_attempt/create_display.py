from flask import Flask, jsonify
import os
import db_connector as db

app = Flask(__name__)

@app.route('/create-db')
def create_database():
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
    return "200"

@app.route('/display-sessions')
def display_sessions():
    db_connection = db.connect_to_database()
    query = f"SELECT sessionID, gym, focus, CAST(sessionDate AS CHAR) as sessionDate FROM TrainingSessions"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    sessionResults = cursor.fetchall()
    query = "SELECT sessionID, COUNT(*) as count FROM Matches GROUP BY sessionID"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    matchResults = cursor.fetchall()
    return [sessionResults, matchResults]


@app.route('/display-session/<int:id>')
def display_session(id):
    db_connection = db.connect_to_database()
    query = f"SELECT sessionID, gym, focus, CAST(sessionDate AS CHAR) as sessionDate FROM TrainingSessions where sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    sessionResults = cursor.fetchall()
    query = f"SELECT matchID, opponent, sessionID FROM Matches where sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    matchResults = cursor.fetchall()
    return [sessionResults, matchResults]



@app.route('/display-match/<int:matchID>')
def display_match(matchID):
    db_connection = db.connect_to_database()
    # query = f"SELECT * FROM Matches WHERE matchID={matchID}"
    query = f"SELECT matchID, opponent, CAST(duration as CHAR) as duration, focus, notes, sessionID FROM Matches WHERE matchID={matchID}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    results = cursor.fetchall()
    results, = results
    return [results]

if __name__=="__main__":
    port = int(os.environ.get('PORT', 9113))
    app.run(port=port, debug=True)