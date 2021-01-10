#
# Copyright 2021 Anders Kaplan
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Tests for the Markdown classes"""

from pytest import raises

from translate.storage import base, markdown

class TestMarkdownTranslationUnitExtraction:
    """
    Test cases based on examples from the [Commonmark
    specification](https://spec.commonmark.org/0.29/), focusing on the
    extraction of translation units.

    These are the principles for extraction:
    1. Extract all content relevant for translation, at the cost of also
       including some formatting.
    2. One translation unit per paragraph.
    3. Keep formatting out of the translation units as much as possible.
    4. Avoid HTML entities in the translation units. Rely on Unicode instead.

    White space within translation units is normalized but hard line breaks are
    preserved. This is because the PO format does not preserve white space, and
    the translated Markdown content will have to be reflowed anyway.
    """

    h = markdown.markdownfile

    def test_example_4(self):
        # A continuation paragraph of a list item is indented with a
        # tab and is interpreted as a list item.
        md = \
r"""
- foo

→bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo", "bar"]

    def test_example_9(self):
        # Nested lists mixing tabs and spaces.
        md = \
r"""
 - foo
   - bar
→ - baz
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo", "bar", "baz"]

    def test_example_12(self):
        # Precedence rules makes this a list with two items, not a
        # list with one item containing a code span.
        md = \
r"""
- `one
- two`
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["`one", "two`"]

    def test_example_13(self):
        # Thematic breaks are not translatable.
        md = \
r"""
***
---
___
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == []

    def test_example_25(self):
        # Examples of strings which are not thematic breaks.
        # Therefore they must be paragraphs, and paragraphs are translatable.
        md = \
r"""
_ _ _ _ a

a------

---a---
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["_ _ _ _ a", "a------", "---a---"]

    def test_example_28(self):
        # Paragraphs split by a thematic break.
        md = \
r"""
Foo
***
bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["Foo", "bar"]

    def test_example_32(self):
        # Basic ATX headings.
        md = \
r"""
# foo
## foo
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo", "foo"]

    def test_example_34_35(self):
        # Paragraphs, not ATX headings.
        md = \
r"""
#5 bolt

#hashtag

\## foo
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["#5 bolt", "#hashtag", "## foo"]

    def test_example_36(self):
        # Inline content in ATX headings counts as inlines.
        md = r"# foo *bar* \*baz\*"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [r"foo *bar* \*baz\*"]

    def test_example_37(self):
        # Leading and trailing whitespace in ATX headings is ignored.
        md = r"#                  foo                     "
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo"]

    def test_example_42(self):
        # ATX headings can have a closing sequence of '#' characters.
        md = r"# foo ##################################"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo"]

    def test_example_44(self):
        # Characters after the closing sequence of an ATX heading disqualifies
        # the closing sequence.
        md = r"### foo ### b"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo ### b"]

    def test_example_49(self):
        # ATX headings can be empty. Empty is not translatable.
        md = \
r"""
## 
#
### ###
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == []

    def test_example_52(self):
        # Multi-line setext heading with inline formatting and leading/trailing whitespace.
        md = \
r"""
  Foo *bar
baz*→
====
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo *bar baz*" ]

    def test_example_60(self):
        # A backslash at the end of a setext heading counts as a literal backslash.
        md = \
r"""
Foo\
----
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo\\" ]

    def test_example_61(self):
        # Setext headings take precedence over code block and embedded html.
        md = \
r"""
`Foo
----
`

<a title="a lot
---
of dashes"/>
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "`Foo", "`", "<a title=\"a lot", "of dashes\"/>" ]

    def test_example_77(self):
        # Code blocks are not translated.
        md = \
r"""
    a simple
      indented code block
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == []

    def test_example_98(self):
        # Block quote with code block. No translatable content.
        md = \
r"""
> ```
> aaa

bbb
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "bbb" ]    

    def test_example_120(self):
        # Asterisks in HTML text are not considered formatting. Leading and trailing whitespace is ignored.
        md = \
r"""
 <div>
  *hello*
         <foo><a>
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "*hello*" ]

    def test_example_122(self):
        # Formatting is removed from markdown blocks when possible.
        md = \
r"""
<DIV CLASS="foo">

*Markdown*

</DIV>
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Markdown" ]

    def test_example_138(self):
        # Raw HTML: leading and trailing HTML tags are stripped from the translatable content.
        md = r"<del>*foo*</del>"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ r"*foo*" ]

    def test_example_139_140_141(self):
        # Script, style, and pre HTML tags are not translatable.
        md = \
r"""
<pre language="haskell"><code>
import Text.HTML.TagSoup

main :: IO ()
main = print $ parseTags tags
</code></pre>
okay
<script type="text/javascript">
// JavaScript example

document.getElementById("demo").innerHTML = "Hello JavaScript!";
</script>
okay
<style
  type="text/css">
h1 {color:red;}

p {color:blue;}
</style>
okay
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "okay", "okay", "okay" ]

    def test_example_161(self):
        # Link reference labels and titles are translatable.
        md = \
r"""
[foo]: /url "title"

[foo]
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "title" ]

    def test_example_165(self):
        # Link titles can extend over multiple lines.
        md = \
r"""
[foo]: /url '
title
line1
line2
'

[foo]
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", \
"""
title
line1
line2
""" ]

    def test_example_171(self):
        # Link titles can contain backslash escapes and literal backslashes.
        md = \
r"""
[foo]: /url\bar\*baz "foo\"bar\baz"

[foo]
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "foo\"bar\\baz" ]

    def test_example_183(self):
        # Heading with a link.
        md = \
r"""
# [Foo]
[foo]: /url
> bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo", "bar" ]

    def test_example_193(self):
        # Leading spaces in paragraphs are ignored.
        md = \
r"""
aaa
             bbb
                                       ccc
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "aaa bbb ccc" ]

    def test_example_196(self):
        # Lines ending with two spaces are considered hard line breaks.
        # Trailing space is stripped from paragraphs, so the last line will not
        # have a hard line break.
        md = \
r"""
aaa     
bbb     
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "aaa\\nbbb" ]

    def test_example_197(self):
        # Blank paragraphs are not translatable.
        md = \
r"""
  

aaa
  

# aaa

  
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "aaa", "aaa" ]

    def test_example_197(self):
        # Block quote with heading.
        md = \
r"""
> # Foo
> bar
> baz
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo", "bar baz" ]

    def test_example_214(self):
        # One translation unit per paragraph, also when wrapped in block quotes.
        md = \
r"""
> foo
>
> bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "bar" ]

    def test_example_226(self):
        # One translation unit per paragraph, also in list items.
        md = \
r"""
- one

  two
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "one", "two" ]

    def test_example_234(self):
        # Code blocks are not translatable, also in list items.
        md = \
r"""
- Foo

      bar


      baz
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo" ]

    def test_example_253(self):
        # Empty list items are not translatable.
        md = \
r"""
1. foo
2.
3. bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "bar" ]

    def test_example_270(self):
        # A list item can contain a heading.
        md = \
r"""
- # Foo
- Bar
  ---
  baz
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "Foo", "Bar", "baz" ]

    def test_example_297(self):
        # Code span:
        # The first backtick matches the second (middle) one, and the third is
        # interpreted as a literal backtick. Hence the formatting cannot be
        # stripped from the translation unit.
        md = r"`hi`lo`"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ r"`hi`lo`" ]

    def test_example_302(self):
        # A backslash at the end of the line means hard line break.
        md = \
r"""
foo\
bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo\nbar" ]

    def test_example_318(self):
        # HTML character entities are converted to unicode.
        md = "[foo](/f&ouml;&ouml; \"f&ouml;&ouml;\")"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "föö" ]

    def test_example_481(self):
        # Inline link text and title are translatable.
        md = "[link](/uri \"title\")"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "link", "title" ]

    def test_example_498(self):
        # A backslash before a non-escapable character is just a backslash.
        md = r"[link](foo\bar)"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ r"foo\bar" ]

    def test_example_512_mod(self):
        # The link text may contain inline content.
        md = r"[*foo **bar** `#`*](/uri)"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ r"foo **bar** `#`" ]

    def test_example_590(self):
        # Autolinks are not translatable.
        md = r"<http://foo.bar.baz>"
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == []

    def test_example_621_mod(self):
        # Leading and trailing raw HTML is excluded from paragraphs.
        md = \
r"""
foo <!-- this is a
comment - with hyphen -->

<!-- this is a
comment - with hyphen --> bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == [ "foo", "bar" ]

    def parse(self, md):
        return self.h.parsestring(md.replace("→", "\t"))

    def get_translation_unit_sources(self, store):
        def getsource(tu):
            return tu.source
        return list(map(getsource, store.units))
