from django.test import TestCase

from inbox.models import WhatsappEstateMessage
from inbox.search_modes import SearchMode, prepare_search
from inbox.search_service import search_listings


class SearchModeTests(TestCase):
    def setUp(self):
        WhatsappEstateMessage.objects.all().delete()

    def _stock(self):
        WhatsappEstateMessage.objects.create(
            raw_body="3 BHK Vesu sell fully furnished 1.1 cr",
            sender_mobile="9999900001",
            message_kind="save",
            estate_status="sell",
            area="vesu",
            number_of_bedrooms=3,
            extracted_json={
                "area": "vesu",
                "estate_status": "sell",
                "furniture": "fully furnished",
                "number_of_bedrooms": 3,
            },
        )

    def _demand(self):
        WhatsappEstateMessage.objects.create(
            raw_body="Required 3 BHK Vesu purchase budget 1cr",
            sender_mobile="9999900002",
            message_kind="save",
            estate_status="buy",
            area="vesu",
            number_of_bedrooms=3,
            extracted_json={
                "area": "vesu",
                "estate_status": "buy",
                "number_of_bedrooms": 3,
            },
        )

    def test_prepare_buyer_ke_liye(self):
        mode, cleaned = prepare_search("khojo buyer ke liye 3bhk vesu buy")
        self.assertEqual(mode, SearchMode.STOCK)
        self.assertIn("vesu", cleaned.lower())

    def test_prepare_kharidar_dhundo(self):
        mode, _ = prepare_search("kharidar dhundo 3bhk vesu")
        self.assertEqual(mode, SearchMode.DEMAND)

    def test_buy_query_finds_sell_listing(self):
        self._stock()
        mode, rows = search_listings("query 3bhk vesu buy fully furnished")
        self.assertEqual(mode, SearchMode.STOCK)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["estate_status"], "sell")

    def test_seller_finds_buyer_requirement(self):
        self._demand()
        mode, rows = search_listings("kharidar dhundo 3bhk vesu")
        self.assertEqual(mode, SearchMode.DEMAND)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["estate_status"], "buy")

    def _rent_listing(self):
        WhatsappEstateMessage.objects.create(
            raw_body="3 BHK Vesu rent 35000 fully furnished",
            sender_mobile="9999900003",
            message_kind="save",
            estate_status="rent",
            area="vesu",
            number_of_bedrooms=3,
            extracted_json={
                "area": "vesu",
                "estate_status": "rent",
                "number_of_bedrooms": 3,
            },
        )

    def _tenant_req(self):
        WhatsappEstateMessage.objects.create(
            raw_body="Tenant required 3 BHK Vesu furnished",
            sender_mobile="9999900004",
            message_kind="save",
            estate_status="rent",
            area="vesu",
            number_of_bedrooms=3,
            extracted_json={
                "area": "vesu",
                "estate_status": "rent",
                "rent_status": "required",
                "number_of_bedrooms": 3,
            },
        )

    def test_rent_lena_finds_listing(self):
        self._rent_listing()
        self._tenant_req()
        mode, rows = search_listings("kiraye par lena 3bhk vesu")
        self.assertEqual(mode, SearchMode.RENT_STOCK)
        self.assertEqual(len(rows), 1)
        self.assertNotIn("required", str(rows[0].get("rent_status", "")))

    def test_tenant_dhundo_finds_requirement(self):
        self._rent_listing()
        self._tenant_req()
        mode, rows = search_listings("tenant dhundo 3bhk vesu")
        self.assertEqual(mode, SearchMode.RENT_DEMAND)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].get("rent_status"), "required")