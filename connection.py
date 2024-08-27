from pymongo import MongoClient

class connection():
  def conn():
    try:
      # url for Mongo DB
      client  = MongoClient('mongodb://localhost:27017/')
      return client['db']
    except Exception as e:
        print("An error occurred while Connection : ", e)
        