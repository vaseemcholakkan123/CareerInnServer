from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from User.models import User, Report, Post
from django.contrib.auth import authenticate
from Employer.models import Department
from rest_framework.viewsets import ModelViewSet
from .serializers import NewsSerializer, AdminDepartmentSerializer , OrderSerializer
from User.views import NormalPagination,SmallPagination
from .models import *
from User.serailizers import ReportSerializer,AdminUserSerializer
from User.signals import post_banned
from django.conf import settings


# Create your views here.


class CheckAuth(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

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
                    prof = settings.BACKEND + user.profile.url
                else:
                    prof = None
                if user.banner:
                    banner = settings.BACKEND + user.banner.url
                else:
                    banner = None
                user_data = {
                    "username": user.username,
                    "info": user.info,
                    "mobile": user.mobile,
                    "location": user.location,
                    "user_id": user.id,
                    "banner": banner,
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


class NewsAction(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer
    pagination_class = NormalPagination
    queryset = News.objects.all()


class DepartmentAction(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminDepartmentSerializer
    queryset = Department.objects.all()
    pagination_class = NormalPagination


class ReportsView(generics.ListAPIView):
    pagination_class = NormalPagination
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request': self.request}
        return serializer_class(*args, **kwargs)


class DeletePost(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, post_id):

        if not post_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No post id provided')

        post = Post.objects.filter(id=post_id)

        if not post.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No post with this id')

        post = post.first()
        # send notification
        post_banned.send(sender=Post, instance=post, deleted=True)

        post.delete()
        return Response(status=status.HTTP_200_OK)


class BlockUser(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user id provided')

        user = User.objects.filter(id=user_id)

        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user with this id')

        user = user.first()
        if not user.is_superuser:
            user.is_blocked = True
            user.save()
            Report.objects.filter(user=user).delete()

        return Response(status=status.HTTP_200_OK)
    
class BlockUserFromList(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user id provided')

        user = User.objects.filter(id=user_id)

        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user with this id')

        user = user.first()
        if not user.is_superuser:
            user.is_blocked = True
            user.save()

        return Response(status=status.HTTP_200_OK)
    
class UnblockUserFromList(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        if not user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user id provided')

        user = User.objects.filter(id=user_id)

        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No user with this id')

        user = user.first()
        if not user.is_superuser:
            user.is_blocked = False
            user.save()

        return Response(status=status.HTTP_200_OK)


class RetrieveUsers(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
    pagination_class = NormalPagination


class GetNews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = News.objects.all()
    serializer_class  = NewsSerializer
    pagination_class = SmallPagination

class GetOrders(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class  = OrderSerializer
    pagination_class = NormalPagination

    def get_queryset(self):
        from_date = self.kwargs.get('from_date')
        to_date = self.kwargs.get('to_date')
        self.queryset = self.queryset.filter(payment_date__range=(from_date,to_date))

        return super().get_queryset()
