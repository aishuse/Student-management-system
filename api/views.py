from django.contrib.auth import authenticate, login, logout
from api.models import Student
from api.serializers import StudentSerializer, LoginSerializer, UserCreationSerializer
from rest_framework import status, authentication, permissions, generics, mixins, throttling
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import BaseThrottle, UserRateThrottle
from pytimeparse.timeparse import timeparse


class ExtendedThrottle(throttling.UserRateThrottle):

    def parse_rate(rate):
        if rate is None:
            return (None, None)
        num, period = rate.split('/')
        num_requests = int(num)
        duration = timeparse(period)
        return (num_requests, duration)

    parse_rate('2/5m')

class UserMinuteThrottle(throttling.UserRateThrottle):
    # scope = "scope_name"

    def parse_rate(self, rate):

        num, period = rate.split('/')
        num_requests = int(num)
        return (num_requests, period*60)

    parse_rate('2/5')


class StudentModelViewset(viewsets.ModelViewSet):
    def get_throttles(self):
        if self.action == 'create':
            throttle_classes = [UserMinuteThrottle]
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