#!flask/bin/python
# -*- coding: utf-8 -*-

import os
import unittest

from config import basedir
from app import app, db
from app.models import JobAd


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
            basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_clean_up_word_list(self):
        caps = JobAd("Sharing is as important as ambition")
        self.assertEqual(caps.clean_up_word_list(),
            ['sharing', 'is', 'as', 'important', 'as', 'ambition'])
        tab = JobAd("Qualities: sharing\tambition")
        self.assertEqual(tab.clean_up_word_list(),
            ['qualities', 'sharing', 'ambition'])
        semicolon = JobAd("Sharing;ambitious")
        self.assertEqual(semicolon.clean_up_word_list(),
            ['sharing', 'ambitious'])
        slash = JobAd(u"Sharing/ambitious")
        self.assertEqual(slash.clean_up_word_list(), ['sharing', 'ambitious'])
        hyphen = JobAd(u"Sharing, co-operative")
        self.assertEqual(hyphen.clean_up_word_list(),
            ['sharing', 'co-operative'])
        mdash = JobAd(u"Sharing—ambitious")
        self.assertEqual(mdash.clean_up_word_list(), ['sharing', 'ambitious'])
        bracket = JobAd(u"Sharing(ambitious")
        self.assertEqual(bracket.clean_up_word_list(), ['sharing', 'ambitious'])
        space = JobAd(u"Sharing ambitious ")
        self.assertEqual(space.clean_up_word_list(), ['sharing', 'ambitious'])
        amp = JobAd(u"Sharing&ambitious, empathy&kindness,")
        self.assertEqual(amp.clean_up_word_list(),
            ['sharing', 'ambitious', 'empathy', 'kindness'])

    def test_extract_coded_words(self):
        j1 = JobAd(u"Ambition:competition–decisiveness, empathy&kindness")
        self.assertEqual(j1.masculine_coded_words,
            "ambition,competition,decisiveness")
        self.assertEqual(j1.masculine_word_count, 3)
        self.assertEqual(j1.feminine_coded_words, "empathy,kindness")
        self.assertEqual(j1.feminine_word_count, 2)
        j2 = JobAd(u"empathy&kindness")
        self.assertEqual(j2.masculine_coded_words, "")
        self.assertEqual(j2.masculine_word_count, 0)
        self.assertEqual(j2.feminine_coded_words, "empathy,kindness")
        self.assertEqual(j2.feminine_word_count, 2)
        j3 = JobAd(u"empathy irrelevant words kindness")
        self.assertEqual(j3.masculine_coded_words, "")
        self.assertEqual(j3.masculine_word_count, 0)
        self.assertEqual(j3.feminine_coded_words, "empathy,kindness")
        self.assertEqual(j3.feminine_word_count, 2)

    def test_assess_coding_neutral_and_empty(self):
        j1 = JobAd("irrelevant words")
        self.assertFalse(j1.masculine_word_count)
        self.assertFalse(j1.feminine_word_count)
        self.assertEqual(j1.coding, "empty")
        j2 = JobAd("sharing versus aggression")
        self.assertEqual(j2.masculine_word_count, j2.feminine_word_count)
        self.assertEqual(j2.coding, "neutral")

    def test_assess_coding_masculine(self):
        j1 = JobAd(u"Ambition:competition–decisiveness, empathy&kindness")
        self.assertEqual(j1.masculine_word_count, 3)
        self.assertEqual(j1.feminine_word_count, 2)
        self.assertEqual(j1.coding, "masculine-coded")
        j2 = JobAd(u"Ambition:competition–decisiveness, other words")
        self.assertEqual(j2.masculine_word_count, 3)
        self.assertEqual(j2.feminine_word_count, 0)
        self.assertEqual(j2.coding, "masculine-coded")
        j3 = JobAd(u"Ambition:competition–decisiveness&leadership, other words")
        self.assertEqual(j3.masculine_word_count, 4)
        self.assertEqual(j3.feminine_word_count, 0)
        self.assertEqual(j3.coding, "strongly masculine-coded")
        # NB: repeated "decisiveness" in j4
        j4 = JobAd(u"Ambition:competition–decisiveness&leadership,"
            " decisiveness, stubborness, sharing and empathy")
        self.assertEqual(j4.masculine_word_count, 6)
        self.assertEqual(j4.feminine_word_count, 2)
        self.assertEqual(j4.coding, "strongly masculine-coded")
        
    def test_assess_coding_feminine(self):
        j1 = JobAd(u"Ambition:competition, empathy&kindness, co-operation")
        self.assertEqual(j1.masculine_word_count, 2)
        self.assertEqual(j1.feminine_word_count, 3)
        self.assertEqual(j1.coding, "feminine-coded")
        j2 = JobAd(u"empathy&kindness, co-operation and some other words")
        self.assertEqual(j2.masculine_word_count, 0)
        self.assertEqual(j2.feminine_word_count, 3)
        self.assertEqual(j2.coding, "feminine-coded")
        j3 = JobAd(u"empathy&kindness, co-operation, trust and other words")
        self.assertEqual(j3.masculine_word_count, 0)
        self.assertEqual(j3.feminine_word_count, 4)
        self.assertEqual(j3.coding, "strongly feminine-coded")
        j4 = JobAd(u"Ambition:competition, empathy&kindness and"
            " responsibility, co-operation, honesty, trust and other words")
        self.assertEqual(j4.masculine_word_count, 2)
        self.assertEqual(j4.feminine_word_count, 6)
        self.assertEqual(j4.coding, "strongly feminine-coded")

    def test_analyse(self):
        j1 = JobAd(u"Ambition:competition–decisiveness&leadership,"
            " decisiveness, stubborness, sharing and empathy")
        self.assertEqual(j1.jobAdText, u"Ambition:competition–decisiveness"
            "&leadership, decisiveness, stubborness, sharing and empathy")
        self.assertTrue(j1.coding == "strongly masculine-coded")
        self.assertEqual(j1.masculine_word_count, 6)
        self.assertEqual(j1.masculine_coded_words, "ambition,competition,"
                "decisiveness,leadership,decisiveness,stubborness")
        self.assertEqual(j1.feminine_word_count, 2)
        self.assertEqual(j1.feminine_coded_words, "sharing,empathy")

if __name__ == '__main__':
    unittest.main()
