# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ast
import io
import operator
import re

from spewe.exceptions import TemplateContextError, TemplateSyntaxError


VAR_TOKEN_START, VAR_TOKEN_END = "{{", "}}"
BLOCK_TOKEN_START, BLOCK_TOKEN_END = "{%", "%}"
TOKEN_REGEX = re.compile(r"(%s.*?%s|%s.*?%s)" % (
    VAR_TOKEN_START, VAR_TOKEN_END, BLOCK_TOKEN_START, BLOCK_TOKEN_END))
WHITESPACE = re.compile('\s+')

TEXT = 0
VAR = 1
BLOCK_START = 2
BLOCK_END = 3
DOT = '.'


def get_possible_names(name):
    parts = name.split(DOT)
    length = len(parts)
    idx = length
    while idx > 0:
        yield idx, DOT.join(parts[:idx])
        idx -= 1


def attr_lookup(obj, attrs):
    if not attrs:
        return obj
    val = getattr(obj, attrs.pop(0))
    if not val:
        return None
    if callable(val):
        val = val()
    return attr_lookup(val, attrs)


def resolve(name, context):
    try:
        return ast.literal_eval(name)
    except (ValueError, SyntaxError):
        pass

    for klen, pkey in get_possible_names(name):
        if pkey in context:
            break
    else:
        raise TemplateContextError(name)

    if name == pkey:
        return context[pkey]
    attrs = name.split(DOT)
    attrs.remove(pkey)
    return attr_lookup(context[pkey], attrs)


class LToken(object):

    def __init__(self, raw_content):
        self.raw_content = raw_content
        self.content = self.clean(raw_content)
        if raw_content.startswith(VAR_TOKEN_START):
            self.content_type = VAR
        elif self.content.startswith('end'):
            self.content_type = BLOCK_END
        elif raw_content.startswith(BLOCK_TOKEN_START):
            self.content_type = BLOCK_START
        else:
            self.content_type = TEXT

    def __repr__(self):
        return '<LToken:%s - %s>' % (self.content_type, self.content)

    def clean(self, raw_content):
        if raw_content.startswith((VAR_TOKEN_START, BLOCK_TOKEN_START)):
            return raw_content[2:-2].strip()
        return raw_content


class Node(object):

    def __init__(self, token=None):
        self.token = token
        self.children = []

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    def render(self, context):
        return ''.join([str(child.render(context)) for child in self.children])


class ScopeNodeMixin(object):
    scope = True


class TextNode(Node):

    def render(self, context):
        return self.token.content


class VarNode(Node):

    def render(self, context):
        content = self.token.content
        return resolve(content, context)


class LoopNode(Node, ScopeNodeMixin):

    def render(self, context):
        content = self.token.content
        items = content.strip().split()[-1]
        if items not in context:
            raise TemplateContextError(items)
        items = context[items]
        rendered = []
        for item in items:
            context['item'] = item
            rendered.append(''.join([str(child.render(context)) for child in self.children]))
        return ''.join(rendered)


class IfNode(Node, ScopeNodeMixin):

    operator_lookup = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        'not': operator.not_
    }

    @staticmethod
    def process_statement(content):
        parts = content.split()[1:]
        if len(parts) not in (1, 3):
            if parts[0] != 'not':
                raise TemplateSyntaxError('<%s>' % content)
        elif len(parts) == 1:
            return parts
        return parts

    def eval_statement(self, stm, context):

        def evaluate(op, *args):
            args = [resolve(hs, context) for hs in args]
            try:
                return self.operator_lookup[op](*args)
            except (KeyError,):
                raise TemplateSyntaxError('operator <%s> is invalid' % op)

        if len(stm) == 1:
            return operator.truth(resolve(stm[0], context))
        elif len(stm) == 2:
            op, args = stm[0], [stm[1]]
        else:
            op, args = stm[1], [stm[0], stm[-1]]
        return evaluate(op, *args)

    def get_branches(self):
        if_branch = []
        else_branch = []
        cur_branch = if_branch  # default branch
        for child in self.children:
            if isinstance(child, (ElseNode,)):
                cur_branch = else_branch
            cur_branch.append(child)
        return if_branch, else_branch

    def render(self, context):
        content = self.token.content
        formatted_statement = self.process_statement(content)
        result = self.eval_statement(formatted_statement, context)
        if_branch, else_branch = self.get_branches()
        if result:
            branch = if_branch
        elif not result and else_branch:
            branch = else_branch
        else:
            return ''
        return ''.join([str(child.render(context)) for child in branch])


class ElseNode(Node, ScopeNodeMixin):
    pass


class TemplateParser(object):

    def __init__(self, template):
        self.template = template
        self.tokens = self._tokenize()
        self.root = Node()

    def _tokenize(self):
        for token in TOKEN_REGEX.split(self.template):
            yield LToken(token)

    def _makenode(self, token):
        content = token.content
        content_type = token.content_type
        if content_type == VAR:
            return VarNode(token)
        if content_type == BLOCK_START:
            statement = content.split()[0]
            if statement == 'loop':
                return LoopNode(token)
            elif statement == 'if':
                return IfNode(token)
            else:
                return ElseNode(token)
        else:
            return TextNode(token)

    def _nodify(self):
        scopes = [self.root]  # rood node
        for token in self.tokens:
            parent_scope = scopes[-1]
            if token.content_type == BLOCK_END:
                scopes.pop()
                continue
            new_node = self._makenode(token)
            parent_scope.children.append(new_node)
            if token.content_type == BLOCK_START:
                scopes.append(new_node)
        return self.root

    def parse(self):
        return self._nodify()


class Template(object):

    def __init__(self, name=None, content=None, context=None):
        self.name = name
        self.content = content
        if not context:
            self.context = {}

    def load(self):
        with io.open(self.name, 'r') as fp:
            self.content = fp.read()
        return True

    @property
    def parser(self):
        return TemplateParser(self.content)

    def render(self, context=None):
        if not self.content and self.name:
            self.load()
        if context:
            self.context.update(context)
        return self.parser.parse().render(context)
