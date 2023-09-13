import pymongo
from bson.objectid import ObjectId

class database():
	

	def __init__(self):
		self.host = "localhost"
		self.port = "27017"
		self.database = "edux"

	def __connect__(self):
		self.client = pymongo.MongoClient("mongodb+srv://mohamedazizsouissi:07244341@cluster0.a51igi5.mongodb.net/?retryWrites=true&w=majority")
		self.db = self.client[self.database]
	
	def __disconnect__(self):
		self.client.close()

	def findall(self, coll, param):
		self.__connect__()
		col = self.db[coll]
		return col.find(param)

	def find(self, coll, param):
		self.__connect__()
		col = self.db[coll]
		return col.find_one(param)
	def view(self,coll):
		self.__connect__()
		col=self.db[coll]
		return col

	def insert(self, data, coll):
		self.__connect__()
		col = self.db[coll]
		try:
			print(col.insert_one(data))
		except Exception as e:
			print(str(e))

	def search(self,txt,coll):
		self.__connect__()
		col = self.db[coll]
		r=col.aggregate([
			{
				"$search":{
					"index":"fdresult",
					"text":{
						"query":txt,
						"path":"result",
						"fuzzy":{}
					}
				}
			}
 		])
		return r

		


	def update(self, key, data,ndata, coll):
		self.__connect__()
		col = self.db[coll]
		try:
			col.find_one_and_update(data,{key:ndata})
			
			return True
		except Exception as e:
			return str(e)

	def delete(self, data, coll):
		self.__connect__()
		col = self.db[coll]
		try:
			col.delete_one(data)
			return True
		except Exception as e:
			return str(e)

	def drop_coll(self, coll):
		self.__connect__()
		col = self.db[coll]
		col.drop()
