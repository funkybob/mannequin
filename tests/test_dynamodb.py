import unittest


from mannequin import models
from mannequin import attrs
from mannequin.stores import dynamodb


class SimpleModel(models.Model):
    name = attrs.StringAttr()
    age = attrs.IntAttr()


SimpleStore = dynamodb.DynamoStore(SimpleModel, hash_key='name')


class DynamoTestCase(unittest.TestCase):
    def test_simple(self):

        obj = SimpleModel(name='Bob', age=42)
        SimpleStore.save(obj)

        obj2 = SimpleStore.get(key='Bob')
        self.assertEqual(obj2.age, 42)
