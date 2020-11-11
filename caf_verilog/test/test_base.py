from unittest import TestCase


class TestCAFBase(TestCase):

    def test_prepended_keys(self):
        if self.__class__.__name__ == 'TestCAFBase':
            return True
        test_class = self.default_base_case()
        test_name = test_class.module_name()
        ttd = test_name.template_dict()

    def default_base_case(self):
        raise NotImplementedError("The %s class has not implemented the prepended keys check" %
                                  type(self).__name__)
