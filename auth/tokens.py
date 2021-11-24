from django.contrib.auth.tokens import PasswordResetTokenGenerator

from six import text_type

## It is used to generate confirmation token or forget password tokens
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.pk) + text_type(timestamp)


generate_token = TokenGenerator()
