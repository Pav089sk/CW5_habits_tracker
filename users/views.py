from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from users.serializers import RegisterUserSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny


User = get_user_model()

class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class RegisterView(CreateAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

