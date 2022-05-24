from rest_framework import status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from .models import User, UserToken
import jwt
from django.conf import settings


# Custom TokenAuthentication Class
class MyOwnTokenAuthentication(TokenAuthentication):

    model = User

    def get_model(self):
        return User

    def authenticate(self, request):
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
            if token=="null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            id = payload['id']
            email = payload['email']
            # print(id)
            # print(email)
            try:
                try:
                    user = User.objects.get(id=id, email=email)
                    # print(user)
                except:
                    msg = {"Status": status.HTTP_404_NOT_FOUND, "detail": "User Not Found"}
                    raise exceptions.AuthenticationFailed(msg)
                try:
                    user_token = UserToken.objects.get(user=user, token=token)
                except:
                    msg = {"Status": status.HTTP_404_NOT_FOUND, "detail": "Token Not Found"}
                    raise exceptions.AuthenticationFailed(msg)

                if not str(token) == str(user_token.token):
                    msg = {"Status": status.HTTP_401_UNAUTHORIZED, "detail": "Token Missmatch"}
                    raise exceptions.AuthenticationFailed(msg)

            except User.DoesNotExist:
                msg = {"Status" :status.HTTP_404_NOT_FOUND, "detail": "User Not Found"}
                raise exceptions.AuthenticationFailed(msg)

        except (jwt.InvalidTokenError,jwt.DecodeError,jwt.ExpiredSignature):
            msg = {"Status" :status.HTTP_401_UNAUTHORIZED, "detail": "Token is invalid"}
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)

    def authenticate_header(self, request):
        return 'Token'