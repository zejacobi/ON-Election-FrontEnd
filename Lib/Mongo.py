"""
All the functions that deal with the Mongo database. These are mostly wrappers, existing so I
don't have to write the same simple code (e.g. for turning a Mongo cursor object into a proper list)
over and over again.
"""

from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

from copy import deepcopy

from Lib.Exceptions import MalformedError
from ExternalServices import DATABASE, MONGO_STRING

client = MongoClient(MONGO_STRING + DATABASE)
database = client[DATABASE]


def insert(json_doc, collection):
    """
    Function for inserting JSON files into a Mongo database

    :note: It appears that pymongo does something incredibly *vile* here; it silently modifies
        the original object with an **_id** field. I get why it needs to add one, but HAVING A
        FUNCTION WITH SUCH A SERIOUS SIDE EFFECT AND NO WARNING IS TERRIBLE. Because of this, I've
        added a deepcopy step, which protects the original document and added this to my test
        cases.
    :note: ObjectID is not a serializable property. So anything saved can no longer be serialized
        by json.dumps, which is, uh, problematic for an API!

    :param dict_or_list json_doc: A valid python dictionary or list of dictionaries, which will be
        converted to the MongoDB BSON format as it is inserted into the database.
    :param str collection: The collection to insert the document into
    :return: The unique ID or IDs given to the inserted item
    :rtype: string_or_list
    """
    json_doc = deepcopy(json_doc)
    if isinstance(json_doc, dict):
        return database[collection].insert_one(json_doc).inserted_id
    elif len(json_doc) == 1:
        return database[collection].insert_one(json_doc[0]).inserted_id
    else:
        return database[collection].insert_many(json_doc).inserted_ids


def find_all(collection):
    """
    Function to find all records in the provided collection

    :param string collection: The name of the database collection
    :return: A list containing all records in the collection
    :rtype: list
    """
    pointer = database[collection].find()
    return [obj for obj in pointer]


def find_subset(collection, query):
    """
    Function to find a subset of the records in the collection, with the subset determine
    by the query.

    :param string collection: The name of the database collection
    :param dict query: A query, potentially limiting the returned records
    :return: A list of all records in the collection that matched the query
    :rtype: list
    """
    pointer = database[collection].find(query)
    return [obj for obj in pointer]


def find_one(collection, query=None):
    """
    Function to find a single record in a collection. If no query is provided, it will return the
    first record based on the natural sort order. Otherwise, it will find the first record based
    on the natural sort order, after filtering the collection based on the query. Deletes the
    **_id** property of the returned dictionary.

    :param string collection: The name of the database collection
    :param dict query: A query, potentially changing the returned record
    :return: A dict containing the first record in the natural ordering based on the search
        criteria. If nothing is found, an empty dict will be returned.
    :rtype: dict
    """
    if query:
        res = database[collection].find_one(query)
    else:
        res = database[collection].find_one()

    if res:
        del res['_id']
        return res
    else:
        return {}


def find_by_id(collection, object_id, literal=False):
    """
    Function to find an object in the database by its unique MongoDB identifier. If you're using
    your own thing as the **_id** of a record, you need to set the literal property to True.
    Otherwise the  *object_id* argument will be cast to the BSON ObjectId type, before being matched
    to the **_id** in the database.

    :param str collection: he name of the database collection
    :param str_or_int object_id: The unique ID (**_id**) of the record you're looking for
    :param bool literal: If true, the *object_id* argument is kept as a whatever it's passed in as.
        Otherwise it is cast to the BSON ObjectID type

    :return: A dict containing the results of the query (if any). If nothing is found, an empty
        dict is returned
    :rtype: dict
    """
    if not literal:
        try:
            object_id = ObjectId(str(object_id))
        except InvalidId:
            raise MalformedError("{} is not a valid literal ObjectID".format(object_id))
    return find_one(collection, {"_id": object_id})
