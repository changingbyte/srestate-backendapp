"""Representative broker WhatsApp copy, including the legacy sample vocabulary."""

from django.test import SimpleTestCase

from inbox.estate_parser import parse_estate_message


class EstateParserTests(SimpleTestCase):
    def test_legacy_and_broker_style_messages_have_two_estate_signals(self):
        cases = [
            ("3bhk flat Citylight rent 22000 furnished", {"area": "city light", "estate_type": "flat", "budget": 22_000}),
            ("Buy flat 52 lac fully furnished garden facing", {"estate_status": "buy", "budget": 5_200_000}),
            ("Required 3 BHK in Vesu budget 1.10 cr", {"area": "vesu", "estate_type": "flat", "budget": 11_000_000}),
            ("2bhk flat for rent at Rajhans Royalton, Vesu, 25k pm", {"estate_status": "rent", "apartment": "rajhans royalton", "budget": 25_000}),
            ("Available 3 BHK semi-furnished at Citylight, rent 30k pm", {"area": "city light", "furniture": "semi furnished"}),
            ("Need to buy rowhouse near Pal Gam, budget 85 lac negotiable", {"area": "pal gam", "estate_type": "row house", "budget": 8_500_000}),
            ("Commercial shop on VIP Road for sale 1.25 cr", {"area": "vip road", "estate_status": "sell"}),
            ("Godam required at Udhna, 1200 sqft", {"area": "udhna", "estate_type": "godown"}),
            ("Resale 4bhk villa at Althan, 2.4 crore", {"area": "althan", "estate_status": "sell"}),
            ("Owner available: 2 BHK at Sangini Lakeville Vesu, 40k pm", {"apartment": "sangini lakeville", "rent_status": "available"}),
            ("New project 3 BHK apartment Bharthana booking open", {"area": "bharthana", "estate_status": "sell"}),
            ("Office on rent, GhodDod road, 850 sq ft", {"area": "ghod dod road", "estate_type": "office"}),
            ("Tenant required for furnished flat in Adjan, 25,000 per month", {"area": "adajan", "furniture": "furnished"}),
            ("Tenement for sale at Mota Varachha 65 lakh", {"area": "mota varachha", "estate_type": "tenament"}),
            ("3 bed penthouse at Piplode for purchase, 1.10 cr", {"area": "piplod", "estate_status": "buy"}),
            ("Industrial shed lease at Sachin? Need warehouse near Palsana", {"estate_type": "industrial shed", "estate_status": "rent"}),
        ]

        for message, expected in cases:
            with self.subTest(message=message):
                parsed = parse_estate_message(message)
                self.assertIsNotNone(parsed)
                for field, value in expected.items():
                    self.assertEqual(parsed.get(field), value)
                signals = ("area", "estate_type", "estate_status", "budget", "number_of_bedrooms", "apartment")
                self.assertGreaterEqual(sum(bool(parsed.get(key)) for key in signals), 2)

    def test_aliases_preserve_bedrooms_and_normalise_values(self):
        parsed = parse_estate_message("3BHK flat citylight sale 85 lac semi-furnished")
        self.assertEqual(parsed["area"], "city light")
        self.assertEqual(parsed["estate_status"], "sell")
        self.assertEqual(parsed["estate_type"], "flat")
        self.assertEqual(parsed["number_of_bedrooms"], 3)
        self.assertEqual(parsed["budget"], 8_500_000)
        self.assertEqual(parsed["furniture"], "semi furnished")

    def test_rejects_non_estate_message(self):
        self.assertIsNone(parse_estate_message("paid 2500 for medicines for mom"))
