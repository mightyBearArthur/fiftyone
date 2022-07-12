import time

from pymongo import MongoClient as PyMongoClient

from fiftyone.core._pymongo_proxy import MongoClient as FiftyOneMongoClient


lcl_client = PyMongoClient("mongodb://localhost:27017")
rmt_client = FiftyOneMongoClient("http://127.0.0.1:8000/_pymongo")

DATABASE_NAME = "fiftytwo"
COLLECTION_NAME = "datasets"


for client in [lcl_client, rmt_client]:
    print(client.__class__.__name__)

    database = client.get_database(DATABASE_NAME)
    dataset = database.get_collection(COLLECTION_NAME).find_one({})
    sample_collection_name = dataset["sample_collection_name"]
    cursor = database.get_collection(sample_collection_name).find({})

    cursor.next()
    for idx, _ in enumerate(cursor):
        if idx > 6:
            break
    print(len(list(cursor)))
