import uuid
from datetime import datetime
from decimal import Decimal

import boto3

from .base import BaseStore

dynamodb = boto3.resource('dynamodb')

import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

class DynamoStore(BaseStore):
    # XXX Provide way to define ProvisionedThroughput
    # XXX Provide way to declare LSI and GSI
    # -> Make them create new storage classes?
    def __init__(self, model, hash_key=None, range_key=None, table=None,
                 with_extra=False):
        super(DynamoStore, self).__init__(model)
        if table is None:
            table = model.__name__
        self.client = dynamodb.Table(table)
        self.table = table
        self.with_extra = with_extra
        # XXX Validate these keys exist in the model fields!
        self.hash_key = hash_key
        assert hash_key in self.model._fields
        self.range_key = range_key
        if range_key is not None:
            assert range_key in self.model._fields

    def _build_key(self, hash_key, range_key=None):
        key = {
            self.hash_key: hash_key,
        }
        if self.range_key:
            key[self.range_key] = range_key
        return key

    def _get_key(self, model):
        key = {
            self.hash_key: getattr(model, self.hash_key),
        }
        if self.range_key:
            key[self.range_key] = getattr(model, self.range_key)
        return key

    def get(self, hash_key, range_key=None):
        if self.range_key and range_key is None:
            raise ValueError(
                'Model {} requires range_key for {}'.format(self.model, self)
            )
        key = self._build_key(hash_key, range_key)

        resp = self.client.get_item(
            Key=key,
            ReturnConsumedCapacity='NONE',
        )

        item = resp.get('Item')
        if not item:
            raise LookupError()
        inst = self.model(**item)
        return inst

    def save(self, model):
        item_data = {}
        for field in self.model._fields:
            try:
                value = getattr(model, field)
            except AttributeError:
                pass
            else:
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    value = str(value)
                elif isinstance(value, float):
                    value = Decimal(value)
                item_data[field] = value
        if self.with_extra and model._extra:
            item_data.update(model._extra)
        self.client.put_item(
            Item=item_data,
            ReturnConsumedCapacity='NONE',
            ReturnItemCollectionMetrics='NONE',
        )

    def delete(self, model):
        key = self._get_key(model)

        self.client.delete_item(
            Key=key,
            ReturnConsumedCapacity='NONE',
            ReturnItemCollectionMetrics='NONE',
        )

    def filter(self, **kwargs):
        index_name = kwargs.pop('_index', None)
        if index_name:
            extra['IndexName'] = index_name
        extra = dict(kwargs)
        resp = self.client.scan(
            ReturnConsumedCapacity='NONE',
            **extra
        )
        items = resp['Items']
        return [
            self.model(**item)
            for item in items
        ]

    def query(self, _index=None, **kwargs):
        if _index:
            kwargs['IndexName'] = _index
        resp = self.client.query(
            ReturnConsumedCapacity='NONE',
            **kwargs
        )
        items = resp['Items']
        return [
            self.model(**item)
            for item in items
        ]
