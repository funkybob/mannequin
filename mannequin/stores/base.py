

class BaseStore(object):
    '''
    Base interface for object Store drivers.
    '''

    def __init__(self, model):
        '''
        Configure a new Store inteface for the given model class.
        '''
        self.model = model

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def save(self, model, **kwargs):
        raise NotImplementedError

    def filter(self, **kwargs):
        raise NotImplementedError
