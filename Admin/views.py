from rest_framework.views import APIView
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser,AllowAny
from User.models import User
from django.contrib.auth import authenticate


# Create your views here.


class CheckAuth(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        if request.user.is_superuser:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class AdminLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_data = request.data.pop("username", None)
        password_data = request.data.pop("password", None)

        if username_data and password_data:


            if '@' in username_data:
                try:
                    usr = User.objects.get(email=username_data)
                    username_data = usr.username
                except:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"message": "No User with this Email !"},
                    )

            user = authenticate(username=username_data, password=password_data)


            if user:

                if not user.is_superuser:
                    return Response(
                        status=status.HTTP_401_UNAUTHORIZED,
                        data={"message": "Not authorized!"},
                    )

                if user.profile:
                    prof = "http://127.0.0.1:8000" + user.profile.url
                else:
                    prof = None
                if user.banner:
                    banner = "http://127.0.0.1:8000" + user.banner.url
                else:
                    banner = None
                user_data = {
                    "username": user.username,
                    "info": user.info,
                    "mobile": user.mobile,
                    "location": user.location,
                    "user_id": user.id,
                    "banner":banner,
                    "profile": prof,
                    "email": user.email,
                }
                return Response(
                    status=status.HTTP_202_ACCEPTED,
                    data={"message": "logged in", "user": user_data},
                )
            else:
                if User.objects.filter(username=username_data).exists():
                    return Response(
                        status=status.HTTP_401_UNAUTHORIZED,
                        data={"message": "Password Wrong !"},
                    )
                else:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={"message": "No Such User !"},
                    )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "credentials not provided"},
            )