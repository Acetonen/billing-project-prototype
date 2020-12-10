from django.urls import path
from rest_framework_jwt.views import RefreshJSONWebToken, VerifyJSONWebToken, ObtainJSONWebToken

from project.accounts.views import RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='api-registration'),
    path('login-web-token/', ObtainJSONWebToken.as_view(), name='api-login'),
    path('refresh-web-token/', RefreshJSONWebToken.as_view(), name='token-refresh'),
    path('verify-web-token/', VerifyJSONWebToken.as_view(), name='token-verify'),
]
