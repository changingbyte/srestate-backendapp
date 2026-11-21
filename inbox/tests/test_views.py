from unittest.mock import patch

from django.test import TestCase, override_settings


@override_settings(
    TWILIO_VALIDATE_SIGNATURE=False,
    FAMILY_ALLOWED_MOBILES=["9123456789"],
)
class WhatsappInboundViewTests(TestCase):
    def test_returns_reply_as_twiml(self):
        response = self.client.post(
            "/whatsapp/inbound/",
            {"From": "whatsapp:+919123456789", "Body": "help", "MessageSid": "SM-test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/xml; charset=utf-8")
        self.assertIn(b"<Response><Message>", response.content)
        self.assertIn(b"Seedhi guide", response.content)
        self.assertNotEqual(response.content, b"<Response></Response>")

    def test_processing_error_still_returns_a_user_reply(self):
        with patch("inbox.views.handle_inbound", side_effect=RuntimeError("database down")):
            response = self.client.post(
                "/whatsapp/inbound/",
                {"From": "whatsapp:+919123456789", "Body": "3bhk vesu sell"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Maaf kijiye".encode(), response.content)

    def test_xml_escapes_reply_text(self):
        with patch("inbox.views.handle_inbound", return_value="3 < 4 & vesu"):
            response = self.client.post(
                "/whatsapp/inbound/",
                {"From": "whatsapp:+919123456789", "Body": "help"},
            )
        self.assertIn(b"3 &lt; 4 &amp; vesu", response.content)
        self.assertNotIn(b"3 < 4", response.content)

    def test_user_text_has_no_mojibake(self):
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        bad = ("\u00e2\u0153", "\u00e2\u20ac", "\u00c3\u00a2")
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in bad:
                self.assertNotIn(token, text, f"{path.name} contains {token}")
