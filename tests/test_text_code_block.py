from xutils.text_parser import TextParser
# 基于 BaseTestCase 的测试代码
import xutils

# cannot perform relative import
try:
    import test_base
except ImportError:
    from tests import test_base

BaseTestCase = test_base.BaseTestCase

class TestTextParser(BaseTestCase):

    def test_code_block_3_backticks(self):
        """测试3个反引号的代码块"""
        parser = TextParser()
        text = '''
这是一段普通文本

```python
print("Hello, World!")
print("This is a test")
```

这是另一段普通文本
'''

        html = parser.render_html(text)
        self.assertIn('<pre class="code-block" data-lang="python"><code>', html)
        self.assertIn('print("Hello, World!")', html)
        self.assertIn('print("This is a test")', html)

    def test_code_block_no_language(self):
        """测试没有语言标签的代码块"""
        parser = TextParser()
        text = '''
```
some code here
```
'''

        html = parser.render_html(text)
        self.assertIn('<pre class="code-block" data-lang=""><code>', html)
        self.assertIn('some code here', html)

    def test_code_block_4_backticks(self):
        """测试4个反引号的代码块"""
        parser = TextParser()
        text = '''
````python
print("Hello, World!")
print("This is a test")
````
'''

        html = parser.render_html(text)
        self.assertIn('<pre class="code-block" data-lang="python"><code>', html)
        self.assertIn('print("Hello, World!")', html)

    def test_code_block_5_backticks(self):
        """测试5个反引号的代码块"""
        parser = TextParser()
        text = '''
`````python
print("Hello, World!")
print("This is a test")
`````
'''

        html = parser.render_html(text)
        self.assertIn('<pre class="code-block" data-lang="python"><code>', html)
        self.assertIn('print("Hello, World!")', html)

    def test_code_block_html_code(self):
        """测试6个反引号的代码块"""
        parser = TextParser()
        text = '''
`````html
<p>Hello, World!</p>
`````
'''

        html = parser.render_html(text)
        self.assertIn('<pre class="code-block" data-lang="html"><code>', html)
        self.assertIn('&lt;p&gt;Hello, World!&lt;/p&gt;', html)
