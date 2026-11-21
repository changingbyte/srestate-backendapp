from django.test import SimpleTestCase

from inbox.intent import Intent, detect_intent


class IntentTests(SimpleTestCase):
    def test_greet(self):
        self.assertEqual(detect_intent("namaste").intent, Intent.GREET)

    def test_list_phrases(self):
        for text in ("meri list", "kya bacha", "aaj ka kaam"):
            self.assertEqual(detect_intent(text).intent, Intent.LIST, text)

    def test_search_natural(self):
        p = detect_intent("khojo adajan 3bhk rent")
        self.assertEqual(p.intent, Intent.SEARCH)
        self.assertIn("adajan", p.remainder.lower())

    def test_assign(self):
        p = detect_intent("de do rahul")
        self.assertEqual(p.intent, Intent.ASSIGN)
        self.assertEqual(p.remainder.lower(), "rahul")

    def test_done_number(self):
        p = detect_intent("ho gaya 7")
        self.assertEqual(p.intent, Intent.DONE)
        self.assertEqual(p.diary_number, 7)

    def test_save_default(self):
        p = detect_intent("3 bhk adajan rent 25000")
        self.assertEqual(p.intent, Intent.SAVE)