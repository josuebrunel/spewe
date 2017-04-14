[![Build Status](https://travis-ci.org/josuebrunel/spewe.svg?branch=master)](https://travis-ci.org/josuebrunel/spewe)
[![Coverage Status](https://coveralls.io/repos/github/josuebrunel/spewe/badge.svg?branch=master)](https://coveralls.io/github/josuebrunel/spewe?branch=master)

SPEWE
=====

Spewe is little Python Web Framework.
Just like spew, this web framework isn't to be used anywhere. Its development is purely educational.
Therefore no need to expect anything Django fancy or whatsoever


## Installation

```shell
$ pip install spewe
```

## Qucik start

This an example of a simple _Hello World_ application

```python
from spewe import Spewe

app = Spewe()


@app.route('/', methods=['GET'], name='index')
def index(request):
    return 'Hello world'


if __name__ == '__main__':
    app.run(port=8099)
```

Voila
