

class Comparable(object):
    def __lt__(self, other):
        return LTNode(self, other)

    def __le__(self, other):
        return LENode(self, other)

    def __eq__(self, other):
        return EQNode(self, other)

    def __ne__(self, other):
        return NENode(self, other)

    def __gt__(self, other):
        return GTNode(self, other)

    def __ge__(self, other):
        return GENode(self, other)


class QNode(Comparable):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

class LTNode(QNode): pass
class LENode(QNode): pass
class EQNode(QNode): pass
class NENode(QNode): pass
class GTNode(QNode): pass
class GENode(QNode): pass
