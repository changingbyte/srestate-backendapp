"""Critical real-life cases: assign order, admin, search, rent, block."""

from django.test import TestCase

from inbox.family_access import ensure_roster, is_family_allowed, operator_mobiles, pick_operator_assignee
from inbox.handlers import handle_inbound
from inbox.models import FamilyMember, LeadRecord

JP = "9328059281"
JITEN = "9327676327"
PRINCE = "7984702696"
SHUBHAM = "6354511915"
JASH = "7069936766"
OUTSIDER = "9000000001"


class CriticalScenarioTests(TestCase):
    def setUp(self):
        ensure_roster()
        LeadRecord.objects.all().delete()

    def test_first_two_saves_jp_then_jitendra(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell 90 lakh")
        handle_inbound(JASH, "Add 2bhk adajan rent 20000")
        got = list(LeadRecord.objects.order_by("id").values_list("assignee_mobile", flat=True))
        self.assertEqual(got, [JP, JITEN])
        self.assertEqual(operator_mobiles()[0], JP)

    def test_query_buy_finds_sell_and_buyer_line_does_not_save(self):
        handle_inbound(PRINCE, "3 BHK Vesu sell fully furnished 1.1 cr")
        n = LeadRecord.objects.count()
        q = handle_inbound(SHUBHAM, "Query 3bhk vesu buy fully furnished")
        self.assertIn("Bik rahi", q)
        self.assertIn("vesu", q.lower())
        b = handle_inbound(JASH, "I have buyer for 3bhk vesu")
        self.assertIn("Bik rahi", b)
        self.assertEqual(LeadRecord.objects.count(), n)

    def test_seller_question_is_search(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell")
        n = LeadRecord.objects.count()
        r = handle_inbound(PRINCE, "Koi seller hai 3bhk ka")
        self.assertNotIn("Save ho gaya", r)
        self.assertEqual(LeadRecord.objects.count(), n)

    def test_rent_lena_vs_tenant(self):
        handle_inbound(SHUBHAM, "Available 3 BHK Vesu rent 35000")
        handle_inbound(JASH, "Tenant required 3 BHK Vesu furnished")
        stay = handle_inbound(PRINCE, "kiraye par lena 3bhk vesu")
        self.assertIn("Kiraye par rehne", stay)
        self.assertNotIn("Tenant required", stay)
        ten = handle_inbound(PRINCE, "tenant dhundo 3bhk vesu")
        self.assertIn("Tenant", ten)

    def test_empty_query_before_save(self):
        r = handle_inbound(PRINCE, "Query 4bhk piplod buy")
        self.assertIn("nahi", r.lower())

    def test_jp_sees_work_and_can_close(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell 80 lakh")
        listing = handle_inbound(JP, "meri list")
        self.assertIn("Vesu", listing)
        done = handle_inbound(JP, "ho gaya")
        self.assertIn("Bahut achha", done)
        self.assertEqual(
            LeadRecord.objects.filter(status=LeadRecord.STATUS_OPEN).count(),
            0,
        )

    def test_manual_reassign_to_named_operator(self):
        handle_inbound(SHUBHAM, "Add 3bhk vesu sell")
        lead = LeadRecord.objects.latest("id")
        other = JITEN if lead.assignee_mobile == JP else JP
        name = "jitendra" if other == JITEN else "jp"
        r = handle_inbound(PRINCE, f"de do {name}")
        self.assertIn("bata diya", r)
        lead.refresh_from_db()
        self.assertEqual(lead.assignee_mobile, other)

    def test_prince_can_block_and_unblock_tester(self):
        self.assertIn("Jash", handle_inbound(PRINCE, "hatado jash"))
        self.assertFalse(is_family_allowed(JASH))
        blocked = handle_inbound(JASH, "meri list")
        self.assertIn("allowed nahi", blocked)
        added = handle_inbound(PRINCE, "jodo 7069936766 Jash")
        self.assertIn("Jash", added)
        self.assertTrue(is_family_allowed(JASH))

    def test_seed_does_not_reactivate_removed_member(self):
        handle_inbound(PRINCE, "hatado shubham")
        ensure_roster()
        self.assertFalse(FamilyMember.objects.get(mobile=SHUBHAM).is_active)

    def test_tester_cannot_remove_and_prince_cannot_remove_self(self):
        self.assertIn("Prince", handle_inbound(SHUBHAM, "hatado jash"))
        self.assertIn("Super admin", handle_inbound(PRINCE, "hatado prince"))
        self.assertTrue(is_family_allowed(PRINCE))

    def test_outsider_blocked(self):
        self.assertIn("allowed nahi", handle_inbound(OUTSIDER, "hi"))

    def test_team_lists_everyone(self):
        text = handle_inbound(JITEN, "team")
        for name in ("JP Halwai", "Jitendra Bajaj", "Prince", "Shubham", "Jash"):
            self.assertIn(name, text)

    def test_round_robin_helper(self):
        self.assertEqual(pick_operator_assignee(), JP)
        LeadRecord.objects.create(
            listing_id=self._listing().id,
            shared_by_mobile=PRINCE,
            assignee_mobile=JP,
            summary="x",
        )
        self.assertEqual(pick_operator_assignee(), JITEN)

    def _listing(self):
        from inbox.models import WhatsappEstateMessage

        return WhatsappEstateMessage.objects.create(
            raw_body="x",
            sender_mobile=PRINCE,
            message_kind="save",
            extracted_json={},
        )
