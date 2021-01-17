.. image:: https://travis-ci.org/josuebrunel/spewe.svg?branch=master
    :target: https://travis-ci.org/josuebrunel/spewe

.. image:: https://coveralls.io/repos/github/josuebrunel/spewe/badge.svg?branch=master
    :target: https://coveralls.io/github/josuebrunel/spewe?branch=master

.. _test_app: /tests/test_app.py#test_form_submission


SPEWE
=====

Spewe is little Python Web Framework.
Just like spew, this web framework isn't to be used anywhere. Its development is purely educational.
Therefore no need to expect anything Django fancy or whatsoever


Installation
------------

.. code:: shell

    $ git clone https://github.com/josuebrunel/spewe.git
    $ python spewe/setup.py install


Quickstart
-----------

This an example of a simple *Hello World* application

.. code:: python

    from spewe import Spewe

    app = Spewe()


    @app.route('/', methods=['GET'], name='index')
    def index(request):
        return 'Hello world'


    if __name__ == '__main__':
        app.run(port=8099)


View with template
^^^^^^^^^^^^^^^^^^

The structure of the application must be as follow:

.. code:: shell

    myapp/
        ├── __init__.py
        ├── templates
        │   └── login.html
        └── views.py

The template directory must be at the same level than your *views.py*.

*views.py*

.. code:: python

    from spewe.http import TempateResponse 

    @testapp.route('/login', methods=['POST'], template='login.html')
    def login(request, *args, **kwargs):
        form = request.form
        context = kwargs['context']
        if form['username'] == 'loking' and form['password'] == 'lokinghd':
            context['authenticated'] = True
            context['username'] = form['username']
        else:
            context['authenticated'] = False
            context['error_message'] = "Invalid credentials"
        return TemplateResponse(context)

To use a template for your view, just pass the template name to *app.route* decorator. When the view will be called, a *context* is passed in *kwargs*.
In order to render the template in the response, a *dict* object has to be returned instead of a *response* object.

*login.html*

.. code:: html

    {% if authenticated %}
    <div class="authenticated">
        <p>Hello {{username.capitalize}} !</p>
    </div>
    {% else %}
    <div class="not-authenticated">
        {% if error_message %}
        <div class="error">{{ error_message }}</div>
        {% endif %}
        <form method="post" action="/login">
            <input type="text" name="username">
            <input type="password" name="password">
            <button type="submit"> Submit </button>
        </form>
    </div>
    {% endif %}


You can check test result in test_app_


Templates
---------

Spewe template engine isn't that different from the common ones

.. code:: python

    class DataClass(object):

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


    class User(DataClass):

        def __repr__(self):
            return "<User: %s>" % self.username

        def info(self):
            return "%s - %s" % (self.username, self.email)

        def is_authenticated(self):
            return self.is_staff


    class Product(DataClass):

        def __repr__(self):
            return "<Product: %s - %s>" % (self.name, self.price)

Let's define a simple context

.. code:: python

    >>> user = User(username='cloking', email='cloking@lk.org',
                fname='chelsea', lname='loking', is_staff=True)

    >>> products = [
        Product(name='orange', price=25), Product(name='apple', price=50),
        Product(name='peach', price=10)
    ]

    >>> context = {'user': user, 'products': products}
    >>> from spewe.template import Template
    >>> tpl = Template('whatever.html')

The template as an html file

.. code:: html

    <html>
        <head>
            <title>Welcome to {{user.fname}} blog</title>
        </head>
        <body>
            {% if not user.is_authenticated %}
            <div class="not-authenticated">
                <p>You need to be authenticated</p>
            </div>
            {% else %}
            <div class="authenticated">
                <div class="user-info">
                    {{user.info}}
                </div>
                <p> Hello {{user.title.capitalize}} {{user.username}} </p>
                <div>
                    Your items above $30 are listed below
                    <ul>
                        {% loop products %}
                            {% if item.price >= 30 %}
                            <li>{{item.name}}: {{item.price}}</li>
                            {% endif %}
                        {% endloop %}
                    </ul>
                </div>
            </div>
            {% endif %}
        </body>
    </html>

Let's render the template

.. code:: python

    In [2]: print(tpl.render(context))
    <html>
        <head>
            <title>Welcome to chelsea blog</title>
        </head>
        <body>

            <div class="authenticated">
                <div class="user-info">
                    cloking - cloking@lk.org
                </div>
                <p> Hello Mme cloking </p>
                <div>
                    Your items above $30 are listed below
                    <ul>
                        <li>apple: 50</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>

    # let's change the user status
    In [3]: user.is_staff = False

    In [4]: print(tpl.render(context))
    <html>
        <head>
            <title>Welcome to chelsea blog</title>
        </head>
        <body>

        <div class="not-authenticated">
            <p>You need to be authenticated</p>
        </div>
    In [5]:
