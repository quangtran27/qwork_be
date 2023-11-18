from firebase_admin import storage

def delete_file(file_url):
  try:
    bucket = storage.bucket()
    file_path = file_url.split('com/')[2]
    print('file_path: ', file_path)
    blob = bucket.blob(file_path)
    print('blob: ', blob)
    blob.delete()
  except:
    pass