import pytest
from webtest import TestApp

from spewe import Spewe


@pytest.fixture
def app():
    app = Spewe()

    @app.route('/index')
    def index(reqest):
        return "this is index"

    return TestApp(app)
