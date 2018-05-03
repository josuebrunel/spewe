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
    form = request.form
    if form['username'] == 'loking' and form['password'] == 'lokinghd':
        response = '<p>User authenticated</p>'
    else:
        response = '<p>User not authenticated</p>'
    return Response(response, status_code=status.HTTP_200_OK)


@testapp.route(r'^/users/(?P<uuid>[\w,-]+)/$')
def users(request, uuid, **kwargs):
    return Response(uuid)
