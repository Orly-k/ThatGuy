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

    def get_event_by_password(self,password):

        return self.event_data.find_one({"password": password})


    def get_event_by_chat_group(self, chat_group):

        return self.event_data.find_one({"group_chat_id": chat_group})


    def set_manager(self, chat_id, password):

        event = self.get_event_by_password(password)
        if event["manager_id"] == "":
            self.event_data.update({"password": password}, {'$set': {"manager_id": chat_id}})
            return True
        else:
            return False


    def set_user_id(self,event_password ,chat_id):

        event = self.get_event_by_password(event_password)

        if chat_id not in event["users_chat_id"]:
            self.event_data.update_one({"password": event_password}, {"$push": {"users_chat_id": chat_id}})

    def add_item_to_list(self, chat_id, item):

        event = self.get_event_by_chat_group(chat_id)

        if item not in event["items"]:
            self.event_data.update_one({"group_chat_id": chat_id}, {"$push": {"items": item}})
            return True
        return False

    def remove_item_from_list(self, chat_id, item):

        logger.info(f"remove_item_from_list {item}")
        event = self.get_event_by_chat_group(chat_id)

        if item in event["items"]:
            self.event_data.update_one({"group_chat_id": chat_id}, {"$pull": {"items": item}})
            return True
        return  False

        event = self.get_event_by_chat_group(chat_id)
        logger.info(f"event[items]:{event['items']} {chat_id} =? {event['group_chat_id']}")

    def set_password(self, chat_id, password):
        logger.info(f"> set_password #{chat_id} #{password}")

        self.event_data.replace_one({"group_chat_id": chat_id}, {
            "group_chat_id": chat_id,
            "manager_id": "",
            "password": password,
            "items": [],
            "users_chat_id": [],
            "expenses": [],
            "responders": [],
            "who_paid": []
        }, upsert=True)