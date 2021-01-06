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
    Test cases based on the [Commonmark
    specification](https://spec.commonmark.org/0.29/), focusing on the
    extraction of translation units.

    The priorities are:
    1. Extract all content relevant for translation.
    2. Keep paragraphs together in the translation units.
    3. Keep formatting out of the translation units as much as possible.
    4. Preserve white space within translation units to the extent possible.
       Leading and trailing space will normally be removed, though, and
       there are no guarantees about white space preservation in later
       processing steps.
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

    def parse(self, md):
        return self.h.parsestring(md.replace("→", "\t"))

    def get_translation_unit_sources(self, store):
        def getsource(tu):
            return tu.source
        return list(map(getsource, store.units))
