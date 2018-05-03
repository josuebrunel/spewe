def test_404(app):
    app.get('/', status=404)


def test_405_method_not_allowed(app):
    app.post('/index', status=405)


def test_response_as_str(app):
    resp = app.get('/index', status=200)
    assert resp.content_type == 'text/plain'
    assert resp.text == 'Hello world from universe !'


def test_form_submission(app):
    payload = {'username': 'loking', 'password': 'lokinghd'}
    resp = app.post('/login', params=payload, status=200)
    assert resp.text == u'<p>User authenticated</p>'


def test_url_argument_parsing(app):
    resp = app.get('/users/120u12a/', status=200)
    assert resp.text == '120u12a'


def test_url_qs_parsing(app):
    resp = app.get('/index/?user=Cartman&from=Southpark')
    assert resp.text == 'Hello Cartman from Southpark !'
