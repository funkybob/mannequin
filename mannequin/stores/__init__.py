
from mannequin import models
from mannequin import attr
from mannequit.stores import botostore


class SimpleModel(models.Model):
    name = attr.StringValue()
    age = attr.IntValue()


SimpleStore = botostore.DynamoStore(SimpleModel, hash_key='name')

obj = SimpleModel(name='Bob', age=42)
SimpleStore.save(obj)
