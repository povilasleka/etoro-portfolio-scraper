from database.connection import db
from database import Position, Portfolio

db.connect()
db.create_tables([Position, Portfolio])
print("Database tables created!")
db.close()