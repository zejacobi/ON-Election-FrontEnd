import unittest

import mongomock

import Lib.Mongo as Mongo

from copy import deepcopy

from Lib.Exceptions import MalformedError


class TestInsert(unittest.TestCase):
    def setUp(self):
        self.Mongo = Mongo
        self.mongo = mongomock.MongoClient()['Test']
        self.Mongo.database = self.mongo

    def test_mock(self):
        """Ensure that the database has been successfully mocked"""
        self.assertEqual(self.Mongo.database.client.address, ('localhost', 27017))

    def test_insert(self):
        """Ensure that the insert function works for a dictionary"""
        self.assertEqual(self.Mongo.insert({"_id": "test"}, 'test'), 'test')
        self.assertEqual(self.mongo['test'].find()[0], {"_id": 'test'})

    def test_insert_side_effects(self):
        """Ensure that the insert function works for a dictionary WITHOUT MUTATING THE FUCKING
            DICT"""
        original = {"test": 1}
        copy = deepcopy(original)
        self.Mongo.insert(original, 'test')
        self.assertEqual(copy, original)

    def test_insert_single_dict_in_array(self):
        """Ensure that the insert function works for a single dict array"""
        self.assertEqual(self.Mongo.insert([{"_id": "test"}], 'test'), 'test')
        self.assertEqual(self.mongo['test'].find()[0], {"_id": 'test'})

    def test_insert_multi_dict_in_array(self):
        """Ensure that the insert function works for a single dict array"""
        ids = ['test', 'test1']
        dicts = [{"_id": ids[0]}, {"_id": ids[1]}]
        self.assertEqual(self.Mongo.insert(dicts, 'test'), ids)
        self.assertEqual(self.mongo['test'].find()[0], dicts[0])
        self.assertEqual(self.mongo['test'].find()[1], dicts[1])


class TestFind(unittest.TestCase):
    def setUp(self):
        self.Mongo = Mongo
        self.collection = 'Test'
        self.mongo = mongomock.MongoClient()[self.collection]
        self.Mongo.database = self.mongo
        self.inserted_docs = [dict(_id=1, data=1), dict(_id=2, data=2), dict(_id=3, data=3)]
        self.mongo[self.collection].insert_many(self.inserted_docs)

    def test_mock(self):
        """Ensure that the database has been successfully mocked"""
        self.assertEqual(self.Mongo.database.client.address, ('localhost', 27017))

    def test_find_all(self):
        """Ensure that find_all returns all inserted records"""
        self.assertEqual(Mongo.find_all(self.collection), self.inserted_docs)

    def test_find_subset(self):
        """Ensure that find_subset returns one the expected results"""
        self.assertEqual(Mongo.find_subset(self.collection, {'_id': {'$lte': 2}}),
                         self.inserted_docs[0:2])

    def test_find_one(self):
        """Ensure that find_one returns the expected document if given no query"""
        self.assertEqual(Mongo.find_one(self.collection), {'data': self.inserted_docs[0]['data']})

    def test_find_one_with_query(self):
        """Ensure that find_one returns the expected document if given a query"""
        self.assertEqual(Mongo.find_one(self.collection, {'data': 2}),
                         {'data': self.inserted_docs[1]['data']})

    def test_find_one_none_found(self):
        """Ensure that find_one returns the expected empty document if it can't find anything"""
        self.assertEqual(Mongo.find_one(self.collection, {'polka_dots': 2}), {})

    def test_find_by_id_literal(self):
        """
        Ensure that find_by_id returns the expected document if given the _id and the literal
        argument=True argument.
        """
        self.assertEqual(Mongo.find_by_id(self.collection, 2, True),
                         {'data': self.inserted_docs[1]['data']})

    def test_find_by_id_oid(self):
        """
        Ensure that find_by_id returns the expected document if given the _id for an objectID
        """
        doc = {'data': 9}
        obj_id = str(self.Mongo.insert({'data': doc['data']}, self.collection))
        self.assertEqual(Mongo.find_by_id(self.collection, obj_id), doc)

    def test_find_by_id_oid_err(self):
        """
        Ensure that find_by_id returns the expected document if given the _id for an objectID
        """
        with self.assertRaises(MalformedError):
            Mongo.find_by_id(self.collection, 'abc')
