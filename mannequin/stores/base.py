from inspect import classify_class_attrs
from ..attr import Attr


class BaseStore(object):
    '''
    Base interface for object Store drivers.
    '''

    def __init__(self, model):
        '''
        Configure a new Store inteface for the given model class.
        '''
        self.model = model
        self.fields = self.get_model_fields(model)

    def get_model_fields(self):
        '''
        Return a map of name : attr for all fields on this model.
        '''
        return {
            name: prop
            for name, kind, cls, prop in classify_class_attrs(self.model)
            if isinstance(prop, Attr)
        }

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, model, **kwargs):
        raise NotImplementedError

    def filter(self, **kwargs):
        raise NotImplementedError
