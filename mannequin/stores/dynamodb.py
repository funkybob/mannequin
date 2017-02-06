import botocore.session

from .. import attrs
from .base import BaseStore


class DynamoStore(BaseStore):
    def __init__(self, model, hash_key=None, range_key=None, table=None,
                 client=None):
        super(DynamoStore, self).__init__(model)
        if client is None:
            session = botocore.session.get_session()
            client = session.create_client('dynamodb')
        self.client = client
        if table is None:
            table = model.__name__
        self.table = table
        # XXX Validate these keys exist in the model fields!
        self.hash_key = hash_key
        assert hash_key in self.model._fields
        self.range_key = range_key
        if range_key is not None:
            assert range_key in self.model._fields

    def get(self, hash_key, range_key=None):
        if self.range_key and range_key is None:
            raise ValueError(
                'Model {} requires range_key for {}'.format(self.model, self)
            )
        key = self.build_key(hash_key, range_key)

        resp = self.client.get_item(
            TableName=self.table,
            Key=key,
        )

        item = resp.get('Item')
        if not item:
            raise KeyError()
        return self.model(**{
            key: value.values()[0]
            for key, value in item.items()
        })

    def save(self, model):
        self.client.put_item(
            TableName=self.table,
            Item={
                field: self.value_for_field(field, getattr(model, field))
                for field in self.model._fields
            }
        )

    def build_key(self, hash_key, range_key):
        key = {
            self.hash_key: self.value_for_field(self.hash_key, hash_key),
        }
        if self.range_key:
            key[self.range_key] = self.value_for_field(self.range_key, range_key)
        return key

    def value_for_field(self, field_name, value):
        return {self.type_for_field(field_name): str(value)}

    def type_for_field(self, field_name):
        field = self.model._fields[field_name]
        if isinstance(field, (attrs.IntAttr, attrs.NumberAttr)):
            return 'N'
        if isinstance(field, attrs.BoolAttr):
            return 'BOOL'
        return 'S'

    def create_table(self):
        '''
        '''
        key_schema = [
            {
                'AttributeName': self.hash_key,
                'KeyType': 'HASH',
            },
        ]
        attr_defs = [
            {
                'AttributeName': self.hash_key,
                'AttributeType': self.type_for_field(self.hash_key),
            }
        ]
        if self.range_key:
            key_schema.append(
                {
                    'AttributeName': self.range_key,
                    'KeyType': 'RANGE',
                }
            )
            attr_defs.append(
                {
                    'AttributeName': self.range_key,
                    'AttributeType': self.type_for_field(self.range_key),
                }
            )

        self.client.create_table(
            TableName=self.table,
            AttributeDefinitions=attr_defs,
            KeySchema=key_schema,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            },
        )
