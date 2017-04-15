import unittest

from mannequin import Model
from mannequin import attrs
from mannequin import query


class TestModel(Model):
    name = attrs.StringAttr()
    age = attrs.IntAttr()


class ExpressionTestCase(unittest.TestCase):

    def test_equality(self):
        x = TestModel.name == 6
        self.assertIsInstance(x, query.QNode)
        self.assertEqual(x.op, '=')
        self.assertEqual(x.lhs, TestModel.name)
        self.assertEqual(x.rhs, 6)

    def test_compound(self):
        x = (TestModel.age > 6) < 12
        self.assertIsInstance(x, query.QNode)
        self.assertEqual(x.op, '<')
        self.assertIsInstance(x.lhs, query.QNode)
        self.assertEqual(x.lhs.op, '>')
        self.assertEqual(x.rhs, 12)
