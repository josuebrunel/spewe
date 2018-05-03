import pytest
from webtest import TestApp


from myapp import testapp


@pytest.fixture
def app():
    return TestApp(testapp)
