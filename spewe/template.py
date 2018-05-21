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

import io
import re

from spewe.exceptions import (TemplateContextError, TemplateNotFound,
                              TemplateSyntaxError, TemplateAttributeError)


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


def evaluate(name, context, if_scope=False):
    try:
        # still not safe though, but it's
        # better a plain and simple eval
        context['__builtins__'] = {}
        result = eval('%s' % name, context)
    except (NameError,):
        if if_scope:
            return False
        raise TemplateContextError(name)
    except (AttributeError,) as exc:
        raise TemplateAttributeError(exc.args[0])
    except (SyntaxError,):
        raise TemplateSyntaxError(name)

    if callable(result):
        result = result()
    return result


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

    def enter_scope(self, stack):
        stack.append(self)
        return stack

    def exit_scope(self, stack):
        stack.pop()
        return stack


class TextNode(Node):

    def render(self, context):
        return self.token.content


class VarNode(Node):

    def render(self, context):
        content = self.token.content
        return evaluate(content, context)


class LoopNode(Node, ScopeNodeMixin):

    endblock_tag = 'endloop'

    def render(self, context):
        content = self.token.content
        iterable_name = content.strip().split()[-1]
        iterable = evaluate(iterable_name, context)
        rendered = []
        for item in iterable:
            context['item'] = item
            rendered.append(''.join([str(child.render(context)) for child in self.children]))
        return ''.join(rendered)


class IfNode(Node, ScopeNodeMixin):

    endblock_tag = 'endif'

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
        content = ' '.join(self.token.content.split()[1:])
        result = evaluate(content, context, if_scope=True)
        if_branch, else_branch = self.get_branches()
        if result:
            branch = if_branch
        elif not result and else_branch:
            branch = else_branch
        else:
            return ''
        return ''.join([str(child.render(context)) for child in branch])


class ElseNode(Node, ScopeNodeMixin):

    endblock_tag = 'endif'

    def exit_scope(self, stack):
        stack = super(ElseNode, self).exit_scope(stack)
        stack.pop()
        return stack


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
                if parent_scope.endblock_tag != token.content:
                    raise TemplateSyntaxError(
                        '<%s> is an invalid opening block for <%s>' % (parent_scope.token.raw_content, token.raw_content))
                parent_scope.exit_scope(scopes)
                continue
            new_node = self._makenode(token)
            parent_scope.children.append(new_node)
            if token.content_type == BLOCK_START:
                new_node.enter_scope(scopes)

        if parent_scope is not self.root:
            raise TemplateSyntaxError('<%s>: block not closed' % parent_scope.token.raw_content)
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
        try:
            with io.open(self.name, 'r') as fp:
                self.content = fp.read()
            return True
        except (IOError,):
            raise TemplateNotFound(self.name)

    @property
    def parser(self):
        return TemplateParser(self.content)

    def render(self, context=None):
        if not self.content and self.name:
            self.load()
        if context:
            self.context.update(context)
        return self.parser.parse().render(context)
