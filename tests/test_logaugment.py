import logging
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import logaugment


class LogaugmentTestCase(unittest.TestCase):

    def setUp(self):
        self.stream = StringIO()
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.StreamHandler(self.stream)
        self.formatter = logging.Formatter(
            "This is the %(message)s: %(custom_key)s")
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.filters = []

    def test_augment_with_dictionary(self):
        logaugment.add(self.logger, {'custom_key': 'new-value'})
        self.logger.info('message')
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: new-value\n")

    def test_augment_with_dictionary_and_extra(self):
        logaugment.add(self.logger, {'custom_key': 'new-value'})
        self.logger.info('message', extra={'custom_key': 'extra-value'})
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: extra-value\n")

    def test_augment_with_callable(self):
        def my_callable(record):
            return {'custom_key': record.filename}

        logaugment.add(self.logger, my_callable)
        self.logger.info('message')
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: test_logaugment.py\n")

    def test_augment_with_callable_dictionary(self):
        class MyDictionary(dict):

            def __call__(self, *args, **kwargs):
                return {'custom_key': 'called_value'}

        my_dict = MyDictionary()
        my_dict['custom_key'] = 'stored_value'
        logaugment.add(self.logger, my_dict)
        self.logger.info('message')
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: called_value\n")

    def test_augment_with_kwargs(self):
        logaugment.add(self.logger, custom_key='new-value')
        self.logger.info('message')
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: new-value\n")

    def test_most_recent_value_is_used(self):
        logaugment.add(self.logger, custom_key='custom-value-1')
        logaugment.add(self.logger, custom_key='custom-value-2')
        self.logger.info('message')
        self.assertEqual(self.stream.getvalue(),
                         "This is the message: custom-value-2\n")
