from django.conf import settings
from django.test import TestCase

from inbox.family_access import ensure_roster
from inbox.handlers import handle_inbound
from inbox.intent import Intent, detect_intent
from inbox.models import LeadRecord, WhatsappEstateMessage


class HandlerTests(TestCase):
    def setUp(self):
        ensure_roster()

    @property
    def mobile(self):
        return settings.FAMILY_ALLOWED_MOBILES[0] if settings.FAMILY_ALLOWED_MOBILES else "9328059281"

    def test_save_listing_creates_lead(self):
        body = "3 BHK Vesu sell fully furnished 1.1 cr"
        self.assertEqual(detect_intent(body).intent, Intent.SAVE)
        reply = handle_inbound(self.mobile, body)
        self.assertIn("Save ho gaya", reply)
        self.assertEqual(WhatsappEstateMessage.objects.count(), 1)
        self.assertEqual(LeadRecord.objects.count(), 1)

    def test_search_keeps_buyer_ke_liye_mode(self):
        WhatsappEstateMessage.objects.create(
            raw_body="3 BHK Vesu sell 1cr",
            sender_mobile=self.mobile,
            message_kind="save",
            estate_status="sell",
            area="vesu",
            number_of_bedrooms=3,
            extracted_json={"area": "vesu", "estate_status": "sell", "number_of_bedrooms": 3},
        )
        reply = handle_inbound(self.mobile, "buyer ke liye 3bhk vesu")
        self.assertIn("Client ko", reply)
        self.assertIn("Bik rahi", reply)

    def test_enquiry_forward_is_save_not_search(self):
        body = "Enquiry 3 bhk vesu buy budget 1 cr"
        self.assertEqual(detect_intent(body).intent, Intent.SAVE)

    def test_user_thread_flow(self):
        mob = self.mobile
        handle_inbound(mob, "Add 3bhk vesu sell fully furnished")
        q = handle_inbound(mob, "Query 3bhk vesu buy fully furnished")
        self.assertIn("Client ko", q)
        self.assertIn("vesu", q.lower())
        self.assertEqual(detect_intent("I have buyer for 3bhk vesu").intent, Intent.SEARCH)
        b = handle_inbound(mob, "I have buyer for 3bhk vesu")
        self.assertIn("Client ko", b)
        self.assertEqual(detect_intent("Koi seller hai 3bhk ka").intent, Intent.SEARCH)