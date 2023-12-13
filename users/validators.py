from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

@deconstructible
class PhoneValidator(validators.RegexValidator):
  regex = r'^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s./0-9]*$'
  message = _('Enter a valid phone number.')
  flags = 0