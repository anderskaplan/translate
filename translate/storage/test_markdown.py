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
    2. Keep formatting out of the translation units as much as possible.
    """

    h = markdown.markdownfile

    def test_example_4(self):
        # Example 4: a continuation paragraph of a list item is indented with a
        # tab and is interpreted as a list item.
        md = \
"""
- foo

→bar
"""
        unit_sources = self.get_translation_unit_sources(self.parse(md))
        assert unit_sources == ["foo", "bar"]

    def parse(self, md):
        return self.h.parsestring(md.replace("→", "\t"))

    def get_translation_unit_sources(self, store):
        def getsource(tu):
            return tu.source
        return list(map(getsource, store.units))
