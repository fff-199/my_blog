import unittest

from django.test.runner import DiscoverRunner


class ExplicitModuleTestRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if test_labels:
            return super().build_suite(test_labels, extra_tests, **kwargs)

        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(loader.loadTestsFromName("blog.comment_tests"))
        if extra_tests:
            suite.addTests(extra_tests)
        return suite

