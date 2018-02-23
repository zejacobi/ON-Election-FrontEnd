import unittest

from Lib.Exceptions import NotFoundError, MalformedError


class TestNotFoundError(unittest.TestCase):
    def test_raisable(self):
        """Test that using the exception with the raise keyword raises an actual exception"""
        with self.assertRaises(NotFoundError):
            raise NotFoundError('This is a test')

    def test_str_representation(self):
        error_str = 'This is a test'
        try:
            raise NotFoundError(error_str)
        except NotFoundError as error:
            self.assertEqual(str(error), error_str)

    def test_int_representation(self):
        error_str = 'This is a test'
        try:
            raise NotFoundError(error_str)
        except NotFoundError as error:
            self.assertEqual(int(error), 404)


class TestMalformedError(unittest.TestCase):
    def test_raisable(self):
        """Test that using the exception with the raise keyword raises an actual exception"""
        with self.assertRaises(MalformedError):
            raise MalformedError('This is a test')

    def test_str_representation(self):
        error_str = 'This is a test'
        try:
            raise MalformedError(error_str)
        except MalformedError as error:
            self.assertEqual(str(error), error_str)

    def test_int_representation(self):
        error_str = 'This is a test'
        try:
            raise MalformedError(error_str)
        except MalformedError as error:
            self.assertEqual(int(error), 400)

