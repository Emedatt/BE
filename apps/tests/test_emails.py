from django.core import mail
from django.test import TestCase, override_settings
from django.conf import settings

# @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailTestCase(TestCase):
    def test_send_email(self):
        """
        Test that an email is sent successfully.
        """
        # Arrange
        subject = 'Test Email'
        message = 'This is a test email from E-MEDATT.'
        recipient_list = [settings.DEFAULT_TO_EMAIL]
        from_email = settings.DEFAULT_FROM_EMAIL

        # Act
        mail.send_mail(subject, message, from_email, recipient_list)
        print("mail senders")

        # Assert
        self.assertEqual(len(mail.outbox), 1)  # Check that one email was sent
        self.assertEqual(mail.outbox[0].subject, subject)  # Check the subject
        self.assertEqual(mail.outbox[0].body, message)  # Check the message body
        self.assertEqual(mail.outbox[0].to, recipient_list)  # Check the recipient list
        self.assertEqual(mail.outbox[0].from_email, from_email) # Check the sender


    def test_email_settings(self):
        self.assertIsNotNone(settings.EMAIL_HOST_USER)
        self.assertIsNotNone(settings.EMAIL_HOST_PASSWORD)
        self.assertIsNotNone(settings.DEFAULT_FROM_EMAIL)
        self.assertIsNotNone(settings.EMAIL_PORT)
        self.assertIsNotNone(settings.EMAIL_HOST)
        self.assertIsNotNone(settings.EMAIL_USE_TLS) \
            or self.assertIsNotNone(settings.EMAIL_USE_SSL)
        self.assertIsNotNone(settings.EMAIL_BACKEND)