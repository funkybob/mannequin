# Mannequin

Models, Storages and Validators, in Python.

## Overview

Models describe only their fields, types, and local methods, along with locally
consistent validation.

Storages adapt models to their particular backing store, adapting according to
the metadata and their own configuration.

Validators operate on Models, or subsets of their fields [or potentially sets
of models, in future] to help validate data.


## Example

```
from mannequin import models
from mannequin import attrs
from mannequin.stores import botostore


class SimpleModel(models.Model):
    name = attrs.StringValue()
    age = attrs.IntValue()


SimpleStore = botostore.DynamoStore(SimpleModel, hash_key='name')

obj = SimpleModel(name='Bob', age=42)
SimpleStore.save(obj)

obj2 = SimpleStore.get(key='Bob')
obj2.age == 42  # True
```
