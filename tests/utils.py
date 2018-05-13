import os


def get_test_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_test_app_template(tplname):
    return os.path.join(get_test_dir(), 'myapp', 'templates', tplname)
