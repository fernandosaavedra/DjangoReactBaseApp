from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from user.messages import PW_RECOVERY_EMAIL_MESSAGE


class PasswordRecoveryMail:
    """ Send email to user for recovering password. """
    def __init__(self, email):
        """ Class initialization """
        self.email_to = email
        self.email_from = settings.EMAIL_HOST_USER

    def send(self):
        """ Send mail with new password to user """
        user = get_user_model().objects.filter(
            email=self.email_to)
        if not user.exists():
            return True
        new_pw = get_user_model().objects.make_random_password()
        # TODO: Pasar nombre de app como variable de entorno.
        title = '[Application] Recuperación de Contraseña'
        html_message = PW_RECOVERY_EMAIL_MESSAGE.format(new_pw)
        has_been_sent = send_mail(
            title, 'Correo enviado', self.email_from, [self.email_to],
            html_message=html_message, fail_silently=False)
        if int(has_been_sent) == 1:
            first_user = user.first()
            first_user.set_password(new_pw)
            first_user.save()
            return True
        else:
            raise AssertionError('Error en cambio de password')
