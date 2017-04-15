import json
import pytest
from webtest import TestApp

from spewe import Spewe, status
from spewe.http import Response


testapp = Spewe()


@testapp.route('/index')
def index(request):
    user = request.params.get('user', ['world'])
    origin = request.params.get('from', ['universe'])
    return "Hello %s from %s !" % (user[0], origin[0])


@testapp.route('/login', methods=['POST'])
def login(request, *args, **kwargs):
    data = json.dumps(request.form)
    return Response(data=data, status_code=status.HTTP_201_CREATED)


@testapp.route(r'^/users/(?P<uuid>[\w,-]+)/$')
def users(request, uuid, **kwargs):
    return Response(uuid)


@pytest.fixture
def app():
    return TestApp(testapp)
