import random

from django.contrib.auth import authenticate, login, logout
from api.models import Student
from api.serializers import StudentSerializer, LoginSerializer, UserCreationSerializer
from rest_framework import status, authentication, permissions, generics, mixins
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import BaseThrottle, UserRateThrottle


# class UserThrottle(UserRateThrottle):
#
#     def parse_rate(self, rate):
#          return (2, 300)

class UserThrottle(BaseThrottle):

    def allow_request(self, request, view):

        return (1, 5)
class StudentModelViewset(viewsets.ModelViewSet):
    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserThrottle]
        else:
            throttle_classes = []  # No throttle for other actions
        return [throttle() for throttle in throttle_classes]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        JWTAuthentication
    ]
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['name', 'age', 'grade']
    ordering_fields = ['name', 'age']



class Registration(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def perform_create(self, serializer):
    #     serializer.save(role='CUSTOMER')


class Login(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                print(token)
                print(created)

                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    def get(self, request):
        logout(request)
        return Response({'msg': 'session ended'})