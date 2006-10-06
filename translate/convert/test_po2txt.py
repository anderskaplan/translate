#!/usr/bin/env python

from translate.convert import po2txt
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po

class TestPO2Txt:
    def po2txt(self, posource, txttemplate):
        """helper that converts po source to txt source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        print inputfile.getvalue()
        outputfile = wStringIO.StringIO()
        templatefile = wStringIO.StringIO(txttemplate)
        assert po2txt.converttxt(inputfile, outputfile, templatefile)
        print outputfile.getvalue()
        return outputfile.getvalue()

    def test_basic(self):
        """test basic conversion"""
        txttemplate = "Heading\n\nBody text"
        posource = 'msgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "Body text"\nmsgstr "Lyfteks"\n'
        assert self.po2txt(posource, txttemplate) == "Opskrif\n\nLyfteks"

    def test_nonascii(self):
        """test conversion with non-ascii text"""
        txttemplate = "Heading\n\nFile content"
        posource = 'msgid "Heading"\nmsgstr "Opskrif"\n\nmsgid "File content"\nmsgstr "Lêerinhoud"\n'
        assert self.po2txt(posource, txttemplate) == "Opskrif\n\nLêerinhoud"


class TestPO2TxtCommand(test_convert.TestConvertCommand, TestPO2Txt):
    """Tests running actual po2txt commands on files"""
    convertmodule = po2txt
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-tTEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "-wWRAP, --wrap=WRAP", last=True)
