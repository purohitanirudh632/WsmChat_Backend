from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken , TokenError
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.db import database_sync_to_async
# import jwt
# from django.conf import settings

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token['user_id']
        return get_user_model().objects.get(id = user_id)
    except:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string  =parse_qs(scope["query_string"].decode())
        token = query_string.get("token")
        if token:
            try:
                validated_token = UntypedToken(token[0])
                scope["user"] = await get_user(validated_token)
                # print(scope["user"],'/n/n/n/n/n/n/n')
            except (InvalidToken , TokenError) as e:
                # print("Invalid_token" , '/n/n/n/n/n/n/n/n')
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()
        close_old_connections()

        return await super().__call__(scope, receive, send)