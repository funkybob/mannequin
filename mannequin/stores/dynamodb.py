import botocore.session

from .. import attrs
from .base import BaseStore


class DynamoStore(BaseStore):
    # XXX Provide way to define ProvisionedThroughput
    # XXX Provide way to declare LSI and GSI
    # -> Make them create new storage classes?
    def __init__(self, model, hash_key=None, range_key=None, table=None,
                 client=None, with_extra=False):
        super(DynamoStore, self).__init__(model)
        if client is None:
            session = botocore.session.get_session()
            client = session.create_client('dynamodb')
        self.client = client
        if table is None:
            table = model.__name__
        self.table = table
        self.with_extra = with_extra
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
        inst = self.model(**{
            key: value.values()[0]
            for key, value in item.items()
        })
        inst._from = self
        return inst

    def save(self, model):
        item_data = {}
        for field in self.model._fields:
            try:
                item_data[field] = self.value_for_field(field, getattr(model, field))
            except AttributeError:
                pass
        if self.with_extra and model._extra:
            item_data.update({
                key: {self.type_for_value(value): str(value)}
                for key, value in model._extra.items()
            })
        self.client.put_item(
            TableName=self.table,
            Item=item_data,
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

    def type_for_value(self, value):
        if isinstance(value, (int, float)):  # Decimal
            return 'N'
        if isinstance(value, bool):
            return 'BOOL'
        if isinstance(value, bytes):
            return 'B'
        if isinstance(value, unicode):
            return 'S'
        if value is None:
            return 'NULL'
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
