from unittest.mock import patch

from django.test import TestCase, override_settings


@override_settings(
    TWILIO_VALIDATE_SIGNATURE=False,
    FAMILY_ALLOWED_MOBILES=["9328059281"],
    WHATSAPP_REPLY_VIA_TWIML=True,
)
class WhatsappInboundViewTests(TestCase):
    def test_help_replies_via_twiml_by_default(self):
        with patch("inbox.views.send_whatsapp") as mock_send:
            response = self.client.post(
                "/whatsapp/inbound/",
                {"From": "whatsapp:+919328059281", "Body": "madad", "MessageSid": "SM1"},
            )
        mock_send.assert_not_called()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Seedhi guide", response.content)
        self.assertIn(b"<Message>", response.content)

    @override_settings(WHATSAPP_REPLY_VIA_TWIML=False)
    def test_rest_ok_returns_empty_twiml(self):
        with patch("inbox.views.send_whatsapp", return_value=(True, "SM99")):
            response = self.client.post(
                "/whatsapp/inbound/",
                {"From": "whatsapp:+919328059281", "Body": "madad", "MessageSid": "SM2"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"<Response></Response>")

    @override_settings(
        TWILIO_VALIDATE_SIGNATURE=True,
        TWILIO_AUTH_TOKEN="secret",
        TWILIO_WEBHOOK_URL="https://princewhatsapp.pythonanywhere.com/whatsapp/inbound/",
    )
    def test_signature_uses_webhook_url(self):
        with patch("inbox.views.RequestValidator") as mock_cls:
            mock_cls.return_value.validate.return_value = True
            response = self.client.post(
                "/whatsapp/inbound/",
                {"From": "whatsapp:+919328059281", "Body": "hi", "MessageSid": "SM3"},
            )
        self.assertEqual(response.status_code, 200)
        mock_cls.return_value.validate.assert_called()
        called_url = mock_cls.return_value.validate.call_args[0][0]
        self.assertEqual(called_url, "https://princewhatsapp.pythonanywhere.com/whatsapp/inbound/")