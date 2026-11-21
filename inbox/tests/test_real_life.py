"""Real numbers — JP, Jitendra, Prince, Shubham, Jash."""

from django.test import TestCase

from inbox.family_access import ensure_roster, operator_mobiles
from inbox.handlers import handle_inbound
from inbox.models import LeadRecord

JP = "9328059281"
JITEN = "9327676327"
PRINCE = "7984702696"
SHUBHAM = "6354511915"
JASH = "7069936766"


class RealLifeScenarioTests(TestCase):
    def setUp(self):
        ensure_roster()
        LeadRecord.objects.all().delete()

    def test_tester_save_goes_to_operator(self):
        reply = handle_inbound(PRINCE, "Add 3bhk vesu sell fully furnished 90 lakh")
        self.assertIn("Kaam", reply)
        lead = LeadRecord.objects.latest("id")
        self.assertIn(lead.assignee_mobile, operator_mobiles())
        self.assertEqual(lead.shared_by_mobile, PRINCE)

    def test_second_save_alternates_operator(self):
        handle_inbound(SHUBHAM, "Add 3bhk adajan sell 50 lakh")
        handle_inbound(JASH, "Add 2bhk vesu rent 25k")
        leads = list(LeadRecord.objects.order_by("id").values_list("assignee_mobile", flat=True))
        self.assertEqual(len(leads), 2)
        if len(operator_mobiles()) >= 2:
            self.assertNotEqual(leads[0], leads[1])

    def test_prince_query_after_save(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell furnished")
        r = handle_inbound(PRINCE, "Query 3bhk vesu buy furnished")
        self.assertIn("Client ko", r)
        self.assertIn("vesu", r.lower())

    def test_buyer_phrase_no_new_lead(self):
        before = LeadRecord.objects.count()
        handle_inbound(PRINCE, "Add 3bhk vesu sell 1cr")
        r = handle_inbound(JASH, "I have buyer for 3bhk vesu")
        self.assertIn("Client ko", r)
        self.assertEqual(LeadRecord.objects.count(), before + 1)

    def test_jp_meri_list_sees_assigned(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell")
        r = handle_inbound(JP, "meri list")
        self.assertIn("Aap par", r)

    def test_team_command(self):
        r = handle_inbound(JASH, "team")
        self.assertIn("JP Halwai", r)
        self.assertIn("Jitendra", r)

    def test_admin_remove_blocked_for_tester(self):
        r = handle_inbound(JASH, "hatado shubham")
        self.assertIn("Prince", r)

    def test_admin_remove_by_prince(self):
        r = handle_inbound(PRINCE, "hatado jash")
        self.assertIn("Jash", r)
        from inbox.family_access import is_family_allowed

        self.assertFalse(is_family_allowed(JASH))