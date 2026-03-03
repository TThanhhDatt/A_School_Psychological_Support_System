from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # nếu dùng file .env

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")

client = MongoClient(MONGO_CONNECTION_STRING)
db = client["therapy_bot_db"]