def test_404(app):
    app.get('/', status=404)


def test_response_as_str(app):
    resp = app.get('/index', status=200)
    assert resp.content_type == 'text/plain'
    assert resp.text == 'this is index'


def test_form_submission(app):
    payload = {'username': 'loking', 'password': 'lokinghd'}
    app.post('/login', params=payload, status=201)


def test_url_argument_parsing(app):
    resp = app.get('/users/120u12a/', status=200)
    assert resp.text == '120u12a'
