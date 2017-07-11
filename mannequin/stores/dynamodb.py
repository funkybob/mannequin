import logging
import uuid
from datetime import datetime, date, time
from decimal import Decimal

import boto3

from .base import BaseStore

dynamodb = boto3.resource('dynamodb')

log = logging.getLogger()
log.setLevel(logging.INFO)


class DynamoStore(BaseStore):
    def __init__(self, model, hash_key=None, range_key=None, table=None,
                 index_name=None, with_extra=False):
        super(DynamoStore, self).__init__(model)
        if table is None:
            table = model.__name__
        self.client = dynamodb.Table(table)
        self.table = table
        self.index_name = index_name
        self.with_extra = with_extra
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
        key = self._build_key(
            self.to_storage(hash_key),
            self.to_storage(range_key),
        )

        resp = self.client.get_item(
            Key=key,
            ReturnConsumedCapacity='NONE',
        )

        item = resp.get('Item')
        if not item:
            raise LookupError()
        inst = self.model(**item)
        return inst

    CASTERS = [
        ((datetime, date, time), lambda x: x.isoformat()),
        (uuid.UUID, str),
        (float, Decimal),
    ]

    def to_storage(self, value):
        for base, func in self.CASTERS:
            if isinstance(value, base):
                return func(value)
        return value

    def save(self, model):
        item_data = {}
        for field in self.model._fields:
            try:
                value = getattr(model, field)
            except AttributeError:
                pass
            else:
                item_data[field] = self.to_storage(value)
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

    def filter(self, *args, **kwargs):
        query = {
            'ReturnConsumedCapacity': 'NONE',
        }

        if self.index_name:
            query['IndexName'] = self.index_name

        # Now convert term expressions.
        # - If field is (hash|range)key, make KeyConditionExpression
        # - Else add to FilterExpression
        # If has KeyCondition, OR index_name, use query
        # XXX Need a way to detect keys of secondary indices
        # Else use scan

        # FilterExpression
        # KeyConditionExpression
        resp = self.client.scan(**query)
        items = resp['Items']
        return [
            self.model(**item)
            for item in items
        ]

    def query(self, **kwargs):
        extra = dict(kwargs)
        if self.index_name:
            extra['IndexName'] = self.index_name

        resp = self.client.query(
            ReturnConsumedCapacity='NONE',
            **extra
        )
        items = resp['Items']
        return [
            self.model(**item)
            for item in items
        ]
