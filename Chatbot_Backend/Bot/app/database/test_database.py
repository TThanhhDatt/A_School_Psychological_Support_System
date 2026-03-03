from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")

# Connection string
uri = MONGO_CONNECTION_STRING

# Tạo client
client = MongoClient(uri)

# Kiểm tra kết nối
try:
    client.admin.command('ping')
    print("Kết nối MongoDB thành công!")
except Exception as e:
    print("Lỗi kết nối:", e)
