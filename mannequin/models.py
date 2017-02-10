from inspect import classify_class_attrs

from .attrs import Attr


class MetaModel(type):
    def __new__(mcs, name, bases, attrs):
        klass = super(MetaModel, mcs).__new__(mcs, name, bases, attrs)

        klass._fields = {
            name: prop
            for name, kind, cls, prop in classify_class_attrs(klass)
            if isinstance(prop, Attr)
        }

        for field in klass._fields:
            getattr(klass, field).name = field
        return klass


class Model(object):
    __metaclass__ = MetaModel

    def __init__(self, **kwargs):
        self._data = {}
        self._extra = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        try:
            return self._extra[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if not name in self._fields and name not in {'_data', '_extra'}:
           self._extra[name] = value
        else:
            super(Model, self).__setattr__(name, value)
