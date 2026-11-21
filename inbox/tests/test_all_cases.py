"""Saare family WhatsApp patterns — galat save / galat search rokna."""

from django.conf import settings
from django.test import TestCase

from inbox.handlers import handle_inbound
from inbox.intent import Intent, detect_intent


def _mob():
    return settings.FAMILY_ALLOWED_MOBILES[0] if settings.FAMILY_ALLOWED_MOBILES else "9328059281"


class AllCaseIntentTests(TestCase):
    """Intent matrix — har line save ya search honi chahiye."""

    def _intent(self, text: str) -> Intent:
        return detect_intent(text).intent

    def test_commands(self):
        cases = {
            "namaste": Intent.GREET,
            "madad": Intent.HELP,
            "meri list": Intent.LIST,
            "ho gaya": Intent.DONE,
            "ho gaya 3": Intent.DONE,
            "de do rahul": Intent.ASSIGN,
            "yaad kal sham phone": Intent.REMIND,
        }
        for text, want in cases.items():
            self.assertEqual(self._intent(text), want, text)

    def test_search_patterns(self):
        for text in (
            "Query 3bhk vesu buy",
            "query 3bhk vesu sell",
            "khojo adajan rent",
            "buyer ke liye 3bhk vesu",
            "kharidar dhundo vesu",
            "kiraye par lena 3bhk adajan",
            "tenant dhundo vesu",
            "I have buyer for 3bhk vesu",
            "Koi seller hai 3bhk ka",
            "looking for 3bhk vesu rent",
            "need 3bhk flat vesu",
            "koi flat hai vesu par",
        ):
            self.assertEqual(self._intent(text), Intent.SEARCH, text)

    def test_save_listings(self):
        self.assertEqual(self._intent("Add 3bhk vesu sell fully furnished"), Intent.MULTI_SAVE)
        for text in (
            "3 BHK Vesu sell 1.10 cr 9328059281",
            "Available 3 BHK Adajan rent 25000 pm",
            "Tenant required 3 BHK Vesu furnished",
            "For sale 4bhk althan 2.4 crore",
            "Resale flat vesu 85 lakh broker 9876543210",
        ):
            self.assertEqual(self._intent(text), Intent.SAVE, text)

    def test_enquiry_forward_save(self):
        self.assertEqual(
            self._intent("Enquiry 3 bhk vesu buy budget 1 cr"),
            Intent.SAVE,
        )

    def test_done_not_inside_listing(self):
        self.assertEqual(
            self._intent("3 BHK Vesu sell fully furnished complete renovation"),
            Intent.SAVE,
        )

    def test_full_thread(self):
        mob = _mob()
        handle_inbound(mob, "Add 3bhk vesu sell fully furnished")
        r1 = handle_inbound(mob, "Query 3bhk vesu buy fully furnished")
        self.assertIn("Client ko dikhane", r1)
        r2 = handle_inbound(mob, "I have buyer for 3bhk vesu")
        self.assertIn("Client ko dikhane", r2)
        self.assertNotIn("Theek hai ji, maine yaad", r2)