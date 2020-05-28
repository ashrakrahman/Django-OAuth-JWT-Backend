from rest_framework.response import Response
from rest_framework import status
from .utils import check_token_validity


def token_authentication_required(view_func):
    def wrap(request, *arg, **kwarg):
        token_string = request.META['HTTP_AUTHORIZATION']
        auth_token = str(token_string).split()

        if len(auth_token) == 1 or len(auth_token) > 2:  # if array size 1 or more than 2
            return Response({"message": "error", "status": "400", "error": "Invalid Header!"}, status=status.HTTP_400_BAD_REQUEST)
        token = auth_token[1]

        is_token_valid = check_token_validity(request, token)

        if is_token_valid == True:
            return view_func(request, *arg, **kwarg)
        else:
            return Response({"message": "error", "status": "403", "error": "Invalid Token!"}, status=status.HTTP_403_FORBIDDEN)
    return wrap
