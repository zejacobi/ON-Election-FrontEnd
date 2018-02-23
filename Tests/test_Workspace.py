import unittest
import os
import json

import Lib.Workspace as Workspace

test_file = os.path.join('.', 'Tests', 'TestData', 'test.json')
json_obj = {"_id": "test"}


class TestParsingJSON(unittest.TestCase):
    """Test the JSON parsing"""
    @classmethod
    def setUpClass(cls):
        """generate the JSON file"""
        with open(test_file, 'w+') as file_obj:
            file_obj.write(json.dumps(json_obj))

    @classmethod
    def tearDownClass(cls):
        """remove the JSON file"""
        os.remove(test_file)

    def test_parse_json(self):
        """Tests that a JSON file is parsed correctly"""
        obj, name = Workspace.parse_json(test_file)
        self.assertDictEqual(obj, json_obj)
        self.assertEqual(name, 'test')
