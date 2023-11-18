import uuid

import magic


def is_valid_uuid(val):
  try:
    uuid.UUID(str(val))
    return True
  except ValueError:
    return False

def is_valid_cv(cv):
  mime = magic.Magic()
  file_mime_type = mime.from_file(cv)
  if file_mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']:
    return True
  else:
    return False
