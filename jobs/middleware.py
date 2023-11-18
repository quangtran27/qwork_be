from requests import Request


def middleware(request):
  response = request

  data = request.data

  description = data['description']
  description.replace('"', '&quot;')

  response.data['description'] = description

  return response