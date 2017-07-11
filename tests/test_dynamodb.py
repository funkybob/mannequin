import unittest

import botocore

from mannequin import models
from mannequin import attrs
from mannequin.stores import dynamodb


session = botocore.session.get_session()
client = session.create_client('dynamodb', endpoint_url='http://localhost:9000')


class SimpleModel(models.Model):
    name = attrs.StringAttr()
    age = attrs.IntAttr()


SimpleStore = dynamodb.DynamoStore(SimpleModel, table="simple", hash_key='name')


class DynamoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # SimpleStore.create_table()
        pass

    def test_simple(self):

        obj = SimpleModel(name='Bob', age=42)
        SimpleStore.save(obj)

        obj2 = SimpleStore.get('Bob')
        self.assertEqual(obj2.age, 42)
