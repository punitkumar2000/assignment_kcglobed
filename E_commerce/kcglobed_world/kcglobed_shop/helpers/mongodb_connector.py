from pymongo import MongoClient

LOCAL_HOST = "mongodb://localhost:27017"
database_name = "contactdetails"
# collection_name = "contactdetails"


class MongoDBConnection:
    def __init__(self, host=LOCAL_HOST, db_name=database_name):
        self.client = MongoClient(host)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]


def mongodb_query_execute(collection_name, query_type=None, data=None, user_filter=None, update_data=None, projection=None):
    connection = MongoDBConnection()
    collection = connection.get_collection(collection_name)

    if query_type == "find":
        if projection:
            return collection.find({}, projection)
        elif user_filter:
            return collection.find({user_filter})
        else:
            return collection.find()
    elif query_type == "find_one":
        return collection.find_one(user_filter)
    elif query_type == "insert_one":
        if data is not None:
            return collection.insert_one(data)
        else:
            raise ValueError("Data is required to insert")
    elif query_type == "insert_many":
        if data is not None:
            return collection.insert_many(data)
        else:
            raise ValueError("Data is required to insert")
    elif query_type == "update_one":
        if user_filter is not None and update_data is not None:
            update_data = {"$set": update_data}
            return collection.update_one(user_filter, update_data)
        else:
            raise ValueError("user_filter and Updated_data are required to update")
    elif query_type == "update_many":
        if user_filter is not None and update_data is not None:
            update_data = {"$set": update_data}
            return collection.update_many(user_filter, update_data)
        else:
            raise ValueError("user_filter and Update_data are required to update")
    elif query_type == "delete_one":
        if user_filter is not None:
            return collection.delete_one(user_filter)
        else:
            raise ValueError("user_filter is required to delete")
    else:
        raise ValueError("Invalid query_type provided.")
