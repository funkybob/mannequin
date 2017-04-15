

class Comparable(object):
    def __lt__(self, other):
        return QNode('<', self, other)

    def __le__(self, other):
        return QNode('<=', self, other)

    def __eq__(self, other):
        return QNode('=', self, other)

    def __ne__(self, other):
        return QNode('!=', self, other)

    def __gt__(self, other):
        return QNode('>', self, other)

    def __ge__(self, other):
        return QNode('>=', self, other)

    def __and__(self, other):
        return QNode('&', self, other)

    def __xor__(self, other):
        return QNode('^', self, other)

    def __or__(self, other):
        return QNode('|', self, other)

    def __rand__(self, other):
        return QNode('&', other, self)

    def __rxor__(self, other):
        return QNode('^', other, self)

    def __ror__(self, other):
        return QNode('|', other, self)


class QNode(Comparable):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
