from peewee import PostgresqlDatabase
import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv('DB_HOST', 'postgres')
print(f"Connecting to database at host: {db_host}")

db = PostgresqlDatabase(
    'postgres',
    user='postgres',
    password='password',
    host=db_host,
    port=5432
)