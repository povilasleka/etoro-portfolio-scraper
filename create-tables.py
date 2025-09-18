from database import db
from models import Position, Portfolio

db.connect()
db.create_tables([Position, Portfolio])
print("Database tables created!")
db.close()