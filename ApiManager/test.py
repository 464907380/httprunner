from django.test import TestCase
from ApiManager.utils import operation


class OperationTests(TestCase):
    def test_add_config_data_with_grammar_error(self):
        """
        为add_config_data添加一个语法有问题的config,返回语法有误的提示
        """


        self.assertIs(operation.add_config_data(False,**congif), False)
