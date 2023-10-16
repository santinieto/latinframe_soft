import unittest


class Test():
    def __init__(self, start_dir='./tests/'):
        self.start_dir = start_dir
        self.tests = []
        self.commands = []

    def get_suite(self, pattern='test_*.py'):
        self.loader = unittest.TestLoader()
        self.suite = self.loader.discover(start_dir=self.start_dir, pattern=pattern)

    def generate_test_command(self, suite):
        if hasattr(suite, '__iter__'):
            for x in suite:
                self.generate_test_command(x)
        else:
            suite_str = str(suite).split()
            testname = suite_str[0]
            classname = suite_str[1].strip("()")
            cmd = f'{self.start_dir[2:-1]}.{classname}.{testname}'
            self.tests.append((cmd, suite))
            #

    def generate_test_list(self):
        self.generate_test_command(self.suite)

        # Crear una tupla que asocie cada elemento con un número
        self.commands = [(i, elemento[0], elemento[1]) for i, elemento in enumerate(self.tests, 1)]

    def show_test_list(self, pattern=None):
        for test in self.commands:
            if ((pattern is None) or
                (pattern in test[1].lower())
            ):
                print(f'- Test {test[0]} : {test[1]}')

    def run(self, sel):
        runner = unittest.TextTestRunner()
        for test in self.commands:
            if test[0] == sel:
                cmd = f'Command: python -m unittest {test[1]}'
                result = runner.run(test[2])