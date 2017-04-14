import json
import pytest
from webtest import TestApp

from spewe import Spewe, status
from spewe.http import Response


testapp = Spewe()


@testapp.route('/index')
def index(reqest):
    return "this is index"


@testapp.route('/login', methods=['POST'])
def login(request, *args, **kwargs):
    data = json.dumps(request.form)
    return Response(data=data, status_code=status.HTTP_201_CREATED)


@pytest.fixture
def app():
    return TestApp(testapp)
