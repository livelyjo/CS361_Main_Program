-- Create table for training sessions
CREATE TABLE TrainingSessions(
    sessionID int not null AUTO_INCREMENT PRIMARY KEY,
    sessionDate DATE not null, 
    gym varchar(255) not null,
    focus varchar(255) not null
);

-- Create table for matches
CREATE TABLE Matches(
    matchID int not null AUTO_INCREMENT PRIMARY KEY,
    opponent varchar(255) not null,
    duration time not null,
    focus varchar(255) not null,
    notes text,
    sessionID int not null,
    FOREIGN KEY (sessionID) REFERENCES TrainingSessions(sessionID)
    on delete cascade
);