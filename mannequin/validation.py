from .attrs import NODEFAULT


class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message

    def __str__(self):
        return 'Invalid[{}]: {}'.format(self.field, self.message)


def validate(data, obj, fields=None, exclude=None):
    errors = {}

    for field in obj._fields:
        if fields and field not in fields:
            continue
        if exclude and field in exclude:
            continue
        if field not in data:
            if obj._fields[field].default is NODEFAULT:
                raise ValidationError(field, 'A value is required')
            continue
        try:
            setattr(obj, field, data[field])
        except (TypeError, ValueError) as e:
            errors[field] = e.args[0]
        except ValidationError as e:
            errors[e.field] = e.message

    return errors
