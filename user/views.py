
from django.http import HttpRequest, HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from user.services import get_google_authorization_url, google_auth



class GoogleAuthorizationURLAPI(APIView):
    @swagger_auto_schema(
        tags=["auth/oauth2"],
        operation_id="Google OAUTH2 Url",
    )
    def get(self, request: HttpRequest) -> Response:
        authorization_url = get_google_authorization_url(request)
        return Response(data={"authorization_url": authorization_url})


class GoogleAuthAPI(APIView):
    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        code = request.GET.get("code")
        error = request.GET.get("error")
        user = google_auth(request, code, error)
        refresh = RefreshToken.for_user(user)
        return Response(
            data={'access': str(refresh.access_token), 'refresh': str(refresh)}
        )
