
class NODEFAULT:
    pass


class Attr(object):
    def __init__(self, null=False, default=NODEFAULT):
        self.name = None
        self.null = null
        self.default = default

    def __get__(self, instance, owner):
        if not instance:
            return self

        try:
            value = instance._data[self.name]
        except KeyError:
            if self.default is NODEFAULT:
                raise AttributeError
            value = self.default
        if value is None and self.null:
            return value
        return self.restore(value)

    def __set__(self, instance, value):
        print(instance, value)
        if instance:
            if not (self.null and value is None):
                value = self.store(value)
            instance._data[self.name] = value

    def store(self, value):
        return value

    def restore(self, value):
        return value


class IntAttr(Attr):

    def store(self, value):
        if isinstance(value, int):
            return value
        return int(value)


class StringAttr(Attr):

    def store(self, value):
        if isinstance(value, unicode):
            return value
        if isinstance(value, str):
            return value.decode('utf-8')
        return unicode(value)


class NumberAttr(Attr):

    def store(self, value):
        if isinstance(value, float):
            return value
        return float(value)


class BoolAttr(Attr):

    def store(self, value):
        return bool(value)
