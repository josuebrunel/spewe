from spewe import Spewe
from spewe.http import Response, JsonResponse


testapp = Spewe()


@testapp.route('/none/')
def none(request):
    return None


@testapp.route('/index')
def index(request):
    user = request.params.get('user', ['world'])
    origin = request.params.get('from', ['universe'])
    return "Hello %s from %s !" % (user[0], origin[0])


@testapp.route('/notemplate/')
@testapp.template('none.html')
def no_template(request, *args, **kwargs):
    return {'none': 'none is none'}


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


@testapp.route(r'^/users/(?P<uuid>[\w,-]+)/notes/', methods=['GET', 'POST'])
@testapp.template('notes.html')
def notes(request, uuid, *args, **kwargs):
    if request.method == 'GET':
        return {}
    context = kwargs.get('context', {})
    return context


@testapp.route(r'^/api/users/$', methods=['get', 'post'])
def api_users(request):
    users = [{'uuid': 'abcd' * 8, 'username': 'cloking', 'email': 'cloking@lk.corp'}]
    if request.method == 'GET':
        return JsonResponse(users)
    if request.json:
        data = request.json
        data['uuid'] = 'aabb' * 8
        users.append(data)
    return JsonResponse(users)
