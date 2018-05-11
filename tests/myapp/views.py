from spewe import Spewe
from spewe.http import Response


testapp = Spewe()


@testapp.route('/index')
def index(request):
    user = request.params.get('user', ['world'])
    origin = request.params.get('from', ['universe'])
    return "Hello %s from %s !" % (user[0], origin[0])


@testapp.route('/login', methods=['POST'])
@testapp.template('login.html')
def login(request, *args, **kwargs):
    form = request.form
    context = kwargs['context']
    if form['username'] == 'loking' and form['password'] == 'lokinghd':
        context['authenticated'] = True
        context['username'] = form['username']
    else:
        context['authenticated'] = False
        context['error_message'] = "Invalid credentials"
    return context


@testapp.route(r'^/users/(?P<uuid>[\w,-]+)/$')
def users(request, uuid, **kwargs):
    return Response(uuid)
