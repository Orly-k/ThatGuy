from pymongo.mongo_client import MongoClient
import logging


logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

class Storage:
    def __init__(self, host, db):
        self.client = MongoClient(host)
        self.db = self.client.get_database(db)
        self.event_data = self.db.get_collection("event_data")

    def create_new_list(self, chat_id):
        self.event_data.replace_one({"chat_id": chat_id}, {
            "chat_id": chat_id,
            "items": [],
        }, upsert=True)

    def set_manager(self,  chat_id):
        self.event_data.replace_one({"manager_chat_id": chat_id}, {
            "manager_chat_id": chat_id,
            "items": [],
        }, upsert=True)

    def add_item_to_list(self, chat_id, item):
        self.event_data.update_one({"chat_id": chat_id}, {"$push": {"items": item}})

    def get_doc(self, chat_id):
        return self.event_data.find_one({"chat_id": chat_id})

    def set_password(self, chat_id, password):
        logger.info(f"> set_password #{chat_id} #{password}")

        self.event_data.replace_one({"chat_id": chat_id}, {
            "chat_id": chat_id,
            "password": password,
        }, upsert=True)
