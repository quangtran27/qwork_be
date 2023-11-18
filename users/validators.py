from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class PhoneValidator(validators.RegexValidator):
  regex = r'\b((\+84|0)(3[2-9]|5[2-9]|7[0|6|7|8|9]|8[1-6|8|9]|9[0-9]))\d{7}\b'
  message = _('Enter a valid phone number.')
  flags = 0