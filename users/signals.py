from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        print(f"📧 Sending activation email to: {instance.email}")

        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_url = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"

        subject = "Activate Your Upohar Account"
        message = f"""
Hello {instance.name},

Welcome to Upohar! Please activate your account by clicking the link below:

{activation_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
Upohar Team
        """

        try:
            send_mail(
                subject=subject,
                message=message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            print(f"✅ Activation email sent to {instance.email}")
        except Exception as e:
            print(f"❌ Failed to send activation email: {e}")
