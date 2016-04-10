from database import dbInterface

db = dbInterface()

pquery = "CREATE TABLE iplpoints \
(matchid integer, game text, playerId integer, points integer)"
tquery = "CREATE TABLE draftPoints \
(id integer primary key, matchid integer, teamId integer, points integer)"

db.send(pquery,[])
db.send(tquery,[])
db.commit()
