from flask import Flask, request
import os
import db_connector as db

app = Flask(__name__)

@app.route('/delete-session', methods=['POST'])
def delete_session():
    db_connection = db.connect_to_database()
    id = request.form.get('delete')
    query = f"DELETE FROM TrainingSessions WHERE sessionID={id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return '200'

@app.route('/delete-match', methods=['POST'])
def delete_match():
    match_id = request.form.get('match_id')
    db_connection = db.connect_to_database()
    query = f"SELECT sessionID FROM Matches WHERE matchID={match_id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    match = cursor.fetchall()
    match, = match
    query = f"DELETE FROM Matches WHERE matchID={match_id}"
    cursor = db.execute_query(db_connection=db_connection, query=query)
    return [match]

if __name__=="__main__":
    port = int(os.environ.get('PORT', 9115))
    app.run(port=port, debug=True)