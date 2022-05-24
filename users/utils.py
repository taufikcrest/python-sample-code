from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions


def Authenticate(self, request):
    auth = get_authorization_header(request).split()
    if not auth or auth[0].lower() != b'token':
        return None

    if len(auth) == 1:
        msg = 'Invalid token header. No credentials provided.'
        raise exceptions.AuthenticationFailed(msg)
    elif len(auth) > 2:
        msg = 'Invalid token header'
        raise exceptions.AuthenticationFailed(msg)

    try:
        token = auth[1]
        if token == "null":
            msg = 'Null token not allowed'
            raise exceptions.AuthenticationFailed(msg)
    except UnicodeError:
        msg = 'Invalid token header. Token string should not contain invalid characters.'
        raise exceptions.AuthenticationFailed(msg)

    return token

