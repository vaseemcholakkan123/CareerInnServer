from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,viewsets,generics,pagination
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from django.core.mail import send_mail
from .serailizers import *
import random
from datetime import datetime,timedelta
from django.conf import settings
from .CustomMixins import *
from Employer.models import Job,Applicant
from Employer.serializers import CompanySerializer,UserJobserializer
from .signals import followNotification

# Create your views here.

# Pagination classes

class NormalPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SmallPagination(pagination.PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 100

# Auth Views

class Validate_Username_Email(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        query_username = request.data.pop("username", None)
        query_email = request.data.pop("email",None)

        
        if User.objects.filter(email=query_email).exists():
            return Response(data={"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=query_username).exists():
            return Response(data={"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_200_OK)

class CreateUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serialize_data = CreateUserSerializer(data=request.data)
        if serialize_data.is_valid():
            new_user = serialize_data.save()
            if new_user:
                subject = 'Account Verification:CarrerInn'
                otp = random.randint(1000,9999)
                message = f'Your Account is created,please verify with this OTP {otp} ,Otp will expire within 5 minutes'
                email_from = settings.EMAIL_HOST
                new_user.otp = otp
                new_user.save()

                send_mail(subject,message,email_from , [new_user.email])
                return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(serialize_data.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
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

                if user.is_blocked:
                    return Response(
                            status=status.HTTP_400_BAD_REQUEST,
                            data={"message": "Account banned"},
                        )

                if not user.is_verified and not user.is_superuser:
                    return Response(
                            status=status.HTTP_400_BAD_REQUEST,
                            data={"message": "Account not verified"},
                        )
                if user.profile:
                    prof = "http://10.4.2.62:8000" + user.profile.url
                else:
                    prof = None
                if user.banner:
                    banner = "http://10.4.2.62:8000" + user.banner.url
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

class VerifyOtp(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        username = request.data.pop('username',None)
        otp = request.data.pop('otp',None)
        print(username,otp)

        if username and otp:

            try:
                if '@' in username:
                    usr = User.objects.get(email=username)
                else:
                    usr = User.objects.get(username=username)
                time = datetime.now().time()
                
                if str(usr.otp) == otp:

                    if time.minute-usr.otp_delay.minute > 5:
                        return Response(
                            status=status.HTTP_400_BAD_REQUEST,
                            data={"message": "Otp Expired"},
                        )

                    usr.is_verified = True
                    usr.save()
                    return Response(
                    status=status.HTTP_202_ACCEPTED,
                    )
                else:
                    return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"message": "Invalid Otp"},
                )
            except:
                return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "credentials not provided"},
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "credentials not provided"},
            )      

class ChangePassword(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        password = self.request.data.get('password',None)
        username = self.request.data.get('username',None)
        print(password,username)
        if not password or not username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if '@' in username:
            user = User.objects.filter(email=username)
        else:
            user = User.objects.filter(username=username)
        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = user.first()

        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_200_OK)
        

class GetNewOtp(APIView):

    permission_classes = [AllowAny]

    def post(self,request):
            
        try:
            query = request.data.pop('username')

            if '@' in query:
                usr = User.objects.get(email=query)

            else:
                usr = User.objects.get(username=query)

            if usr.otp_limit >= 12:
                 return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"message": "Otp Limit Ended ,please try with another mail!"},
                )

            subject = 'Account Verification:CarrerInn'  
            otp = random.randint(1000,9999)
            message = f'Your Account is created,please verify with this OTP {otp},Otp will expire within 5 minutes'
            email_from = settings.EMAIL_HOST
            usr.otp = otp
            usr.otp_limit += 1 
            usr.save()
            send_mail(subject,message,email_from , [usr.email])
            return Response(
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "credentials not provided"},
            )

class GetForReset(APIView):

    permission_classes = [AllowAny]

    def post(self,request):
            
        try:
            query = request.data.pop('username')

            if '@' in query:
                usr = User.objects.filter(email=query)

            else:
                usr = User.objects.filter(username=query)

            if not usr.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST,data='No such user')
            usr = usr.first()


            subject = 'Password Reset :CarrerInn'  
            otp = random.randint(1000,9999)
            message = f'Your OTP for password reset,please verify with this OTP {otp},Otp will expire within 5 minutes'
            email_from = settings.EMAIL_HOST
            usr.otp = otp
            
            usr.save()
            send_mail(subject,message,email_from , [usr.email])
            return Response(
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                status=status.HTTP_502_BAD_GATEWAY,
                data={"message": "credentials not provided"},
            ) 



class Logout(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh-token"])
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "Token Not Provided"},
            )

#  User Actions 

class ChangeDetails(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        form = request.data.get('details')
        if not form:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'details not provided'})

        if form['username'] != request.user.username:
            print('sertinf username')
            request.user.username = form['username']

        
        if form['info']:
            request.user.info = form['info']

        if form['mobile']:
            request.user.mobile = form['mobile']

        if form['location']:
            request.user.location = form['location']

        try:
            request.user.save()
            if request.user.banner:
                banner = "http://10.4.2.62:8000" + request.user.banner.url
            else:
                banner = None
            user_data = {
                    "username": request.user.username,
                    "info":request.user.info,
                    "mobile":request.user.mobile,
                    "location":request.user.location,
                    "user_id": request.user.id,
                    "banner":banner,
                    "profile": "http://10.4.2.62:8000" + request.user.profile.url,
                    "email": request.user.email,
                }
            return Response(status=status.HTTP_200_OK,data={'user':user_data})
        except Exception as e:
            return Response(status=status.HTTP_409_CONFLICT,data={'message':'Internal error','error':e})
        
class ChangeProfilePicture(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        profile = request.data.get('profile')
        if not profile:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No embedded profile')
        request.user.profile.save(profile.name, profile, save=True)
        if request.user.banner:
            banner = "http://10.4.2.62:8000" + request.user.banner.url
        else:
            banner = None
        user_data = {
                    "username": request.user.username,
                    "info":request.user.info,
                    "mobile":request.user.mobile,
                    "location":request.user.location,
                    "user_id": request.user.id,
                    "banner":banner,
                    "profile": "http://10.4.2.62:8000" + request.user.profile.url,
                    "email": request.user.email,
                }
        return Response(status=status.HTTP_200_OK,data={'user':user_data})

class ChangeProfileBanner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        banner = request.data.get('banner')
        if not banner:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No embedded banner')
        request.user.banner.save(banner.name, banner, save=True)

        if request.user.profile:
            prof = "http://10.4.2.62:8000" + request.user.profile.url
        else:
            prof = None
        user_data = {
                    "username": request.user.username,
                    "info":request.user.info,
                    "mobile":request.user.mobile,
                    "location":request.user.location,
                    "user_id": request.user.id,
                    "profile": prof,
                    "banner": "http://10.4.2.62:8000" + request.user.banner.url,
                    "email": request.user.email,
                }
        return Response(status=status.HTTP_200_OK,data={'user':user_data})

class SearchUser(APIView):

    permission_classes = [AllowAny]
    
    def post(self,request):
        query = request.data.get("query",None)
        if not query:
            return Response(status=status.HTTP_404_NOT_FOUND,data='No query to populate data')

        user = User.objects.filter(username__icontains=query)

        if not user.exists():
            return Response(status=status.HTTP_200_OK,data='no data')

        user = UserSerializer(user,many=True).data

        return Response(status=status.HTTP_200_OK,data=user)

class CheckCompanyRelation(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        if self.request.user.company:
            return Response(status=status.HTTP_200_OK,data={'var':'continue','id':self.request.user.company.id})
        return Response(status=status.HTTP_200_OK,data={'var':'register'})
    
class GetCompany(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        if self.request.user.company:
            company = CompanySerializer(self.request.user.company,many=False).data
            return Response(status=status.HTTP_200_OK,data={'company':company})
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

class AddProject(generics.CreateAPIView):
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CreateProjectSerializer

    def create(self, request, *args, **kwargs):
        if Project.objects.filter(user=request.user,name=request.data.get('name')).exists():
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED,data={'message':'Already posted this project'})
        
        return super().create(request, *args, **kwargs)

class RetrieveProject(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetrieveProjectSerializer

    def get_queryset(self):
        self.queryset = Project.objects.filter(user=self.request.user)
        return super().get_queryset()

class UpdateProject(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = CreateProjectSerializer
    queryset = Project.objects.all()

    def perform_update(self, serializer):
        if not serializer.validated_data.get('user') == self.request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED,data={'message':'Not Authorized'})
        return super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        
        if not instance.user == self.request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED,data={'message':'Not Authorized'})
        return super().perform_destroy(instance)
    
class RetrieveDifferPost(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = postsSeriallizer
    queryset = Post.objects.all()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)

class FollowUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target = request.data.get('user_id')
        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'target id not found'})

        target = User.objects.filter(id=target)

        if target.exists():
            target = target.first()
            thread = connections.objects.filter(user=request.user,following=target)

            if thread.exists():
                thread.first().delete()
                return Response(status=status.HTTP_200_OK)
            else:
                print('exists not creating one')

                c = connections.objects.create(user=request.user)
                c.following.add(target)
                c.save()
                followNotification.send(sender=connections,instance=c,created=True,target=target)
                return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'no user with the target id'})

class BreakFollowingUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target = request.data.get('user_id')
        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'target id not found'})

        target = User.objects.filter(id=target)

        if target.exists():
            target = target.first()
            thread = connections.objects.filter(user=target,following=request.user)

            if thread.exists():
                thread.first().delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'no user with the target id'})


class UserFollowers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerSerializer
    pagination_class = NormalPagination

    def get_queryset(self):
        self.queryset = connections.objects.filter(following__in=[self.request.user.id])
        return super().get_queryset()
    
class FollowingUsers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowingSerializer
    pagination_class = NormalPagination

    def get_queryset(self):
        self.queryset = connections.objects.filter(user=self.request.user)
        return super().get_queryset()


class AddUserSkill(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        skill = request.data.get('skill_id',None)

        if not skill:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No id to populate data')

        skill = Skill.objects.filter(id=skill)
        if not skill.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='No skill with this id')
        skill = skill.first()
        
        usr = request.user

        if skill in usr.skills.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'exixts':'Already added this skill'})

        usr.skills.add(skill)
        usr.save()

        return Response(status=status.HTTP_200_OK)

class RemoveUserSkill(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        skill = request.data.get('skill_id',None)

        if not skill:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No id to populate data')

        skill = Skill.objects.filter(id=skill)
        if not skill.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='No skill with this id')
        skill = skill.first()
        
        usr = request.user

        if skill not in usr.skills.all():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'not_exixts':'skill not in user skills'})

        usr.skills.remove(skill)
        usr.save()

        return Response(status=status.HTTP_200_OK)

class RetrieveUserJobs(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserJobserializer
    pagination_class = NormalPagination

    def get_queryset(self):
        applications = Applicant.objects.filter(user=self.request.user)
        self.queryset = Job.objects.filter(applicants__in=applications)
        return super().get_queryset()
    

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)

class RetrieveNotifications(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NormalPagination

    def get_queryset(self):
        self.queryset = Notification.objects.filter(user=self.request.user,is_read=False).order_by('-created')
        return super().get_queryset()
    
class RetrieveReadNotifications(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NormalPagination

    def get_queryset(self):
        self.queryset = Notification.objects.filter(user=self.request.user,is_read=True).order_by('-created')
        return super().get_queryset()

class DeleteNotification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target = request.data.get('notification_id')

        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No notification id')

        target = Notification.objects.filter(id=target)

        if not target.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No notification with this id')

        target = target.first().delete()

        return Response(status=status.HTTP_200_OK)
    
class MarkALLAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        notifications_bucket = Notification.objects.filter(user=request.user)

        if not notifications_bucket:
            return Response(status=status.HTTP_200_OK)

        for n in notifications_bucket:
            n.is_read = True
            n.save()

        return Response(status=status.HTTP_200_OK)
        


class ReadNotification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target = request.data.get("notification_id",None)
        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No id to populate data')

        target = Notification.objects.filter(id=target,user=request.user)

        if not target.exists():
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data='No notification with this id')

        target = target.first()

        target.is_read = True
        target.save()
        return Response(status=status.HTTP_200_OK)


class RetrieveUserSkills(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer

    def get_queryset(self):
        self.queryset = self.request.user.skills.all()
        return super().get_queryset()

class ReportPost(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateReportSerializer
    queryset = Report.objects.all()

    def post(self,request):
        request.data['user'] = request.user.id
        return super().post(request)
    
class SaveUnsavePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user_bucket = SavedPosts.objects.filter(user=request.user)
        target_post = request.data.get("post_id",None)

        if not target_post:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no target post id')

        target_post = Post.objects.filter(id=target_post)

        if not target_post.exists():
            return Response(status.HTTP_400_BAD_REQUEST,data='No post with this id')

        target_post = target_post.first()

        if user_bucket.exists():
            user_bucket = user_bucket.first()
        else:
            user_bucket = SavedPosts.objects.create(user=request.user)
        action = ''

        if user_bucket.post.filter(id=target_post.id).exists():
            user_bucket.post.remove(target_post)
            action = 'unsaved'
        else:
            action = 'saved'
            user_bucket.post.add(target_post)

        return Response(status=status.HTTP_200_OK,data=action)
# Post Views


class CommentsPagination(pagination.PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostsView(PostsMixin,viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = postsSeriallizer
    pagination_class = NormalPagination

    def perform_create(self, serializer):
        serializer.save(posted_user=self.request.user)
        return Response(status=status.HTTP_200_OK)
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)
    

class GetUserPosts(PostsMixin,generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = postsSeriallizer
    pagination_class = NormalPagination

    def perform_create(self, serializer):
        serializer.save(posted_user=self.request.user)
        return Response(status=status.HTTP_200_OK)
    
    def get_queryset(self):
        self.queryset = Post.objects.filter(posted_user=self.request.user)
        return super().get_queryset()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)
    

class GetDifferentUserPosts(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = postsSeriallizer
    pagination_class = NormalPagination

    def get_queryset(self):
        self.queryset = Post.objects.filter(posted_user__id=self.kwargs['user_id'])
        return super().get_queryset()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)
    
# class GetSavedPosts(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = SavedPostsSerializer
#     pagination_class = NormalPagination

#     def get_queryset(self):
#         self.queryset = SavedPosts.objects.filter(user=self.request.user)
#         return super().get_queryset()

#     def get_serializer(self, *args, **kwargs):
#         serializer_class = self.get_serializer_class()
#         kwargs.setdefault('context', self.get_serializer_context())
#         kwargs['context'] = {'request':self.request}
#         return serializer_class(*args, **kwargs)

class GetSavedPosts(APIView):  
    permission_classes = [AllowAny]
    pagination_class = NormalPagination

    def get_queryset(self):
        # Get posts for the current user
        return SavedPosts.objects.filter(user=self.request.user)
    
    def get(self, request, **kwargs):
        saved_posts = self.get_queryset()

        # Get all related posts for each SavedPosts instance
        posts_list = [saved_post.post.all() for saved_post in saved_posts]

        # Flatten the list of posts
        posts = [post for sublist in posts_list for post in sublist]

        # Manually paginate the flattened posts
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)

        # Serialize the paginated posts using the PostSerializer
        serializer = postsSeriallizer(paginated_posts, many=True, context={'request': request})

        return paginator.get_paginated_response(serializer.data)

class PeopleKnow(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = SmallPagination
    serializer_class = UserSerializer

    def get_queryset(self):
        usr = self.request.user
        usr_bucket = connections.objects.filter(user=usr)
        p_n = []

        for c in usr_bucket:
            f_users = connections.objects.filter(following=c.following.first())
            for u in f_users:
                if u.user != usr:
                    if not u.user in p_n:
                        p_n.append(u.user)

        if len(p_n) > 5 :
            self.queryset =  p_n

        else:
            for x in User.objects.all():
                if not connections.objects.filter(user=usr,following=x).exists():
                    if x not in p_n and x != usr:
                        p_n.append(x)

            self.queryset = p_n

        return super().get_queryset()


class AddComment(APIView):  
    permission_classes = [AllowAny]
    
    def post(self,request,**kwargs):
        post_id = kwargs['post_id']
        query_comment = request.data.pop('comment')

        if not query_comment or query_comment == '':
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'comment not provided or is empty'})

        if not post_id:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'Post id not provided'})

        try:
            query_post = Post.objects.get(id = post_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'Cannot find a post with this id'}) 

        d = comment.objects.create(post=query_post,user=request.user,comment_text=query_comment)

        return Response(status=status.HTTP_201_CREATED,data=d.id)


class GetPostComments(generics.ListAPIView):
    permission_classes  = [AllowAny]
    pagination_class = CommentsPagination
    serializer_class = commentSerializer

    def get(self, request, *args, **kwargs):

        post_id = kwargs['post_id']

        if not post_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.queryset = comment.objects.by_post(post_id=post_id)
        return super().get(request, *args, **kwargs)

class DeleteComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,**kwargs):

        comment_kwarg = kwargs['comment_id']
        if not comment_kwarg:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'Comment id not provided'})

        try:
            c = comment.objects.get(id=comment_kwarg)

            if not c.user == request.user:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            c.delete()
            return Response(status=status.HTTP_200_OK) 
        except:
            return Response(status=status.HTTP_404_NOT_FOUND,data={'message':'No such comment'})

class LikePost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,**kwargs):

        post_id = kwargs['post_id']
        try:
            query_post = Post.objects.get(id=post_id)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'message':'Post id not provided'})

        Like_obj = Like.objects.filter(user=request.user,post=query_post)

        if not Like_obj.exists():
            Like.objects.create(user=request.user,post=query_post,liked=True)
            query_post.likes += 1
            query_post.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            Like_obj = Like_obj.first()

        if not Like_obj.liked:
            Like_obj.liked = True
            Like_obj.save()

            query_post.likes += 1
            query_post.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        
        else:
            Like_obj.liked = False
            Like_obj.save()

            query_post.likes -= 1
            query_post.save()
            return Response(status=status.HTTP_202_ACCEPTED)
            

#  other

class CreateSkills(generics.CreateAPIView):
    queryset = Skill.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer

class AddEducation(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

class UpdateEducation(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = EducationSerializer
    queryset = Education.objects.all()

    def put(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().put(request, *args, **kwargs)

class AddExperience(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().create(request, *args, **kwargs)

class UpdateExperience(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = ExperienceSerializer
    queryset = Experience.objects.all()

    def put(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super().put(request, *args, **kwargs)


class RetrieveUserExperence(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetrieveExpSerializer
    def get_queryset(self):
        self.queryset = Experience.objects.filter(user=self.request.user)
        return super().get_queryset()

class RetrieveUserEducation(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EducationSerializer
    def get_queryset(self):
        self.queryset = Education.objects.filter(user=self.request.user)
        return super().get_queryset()


class SearchSkills(APIView):

    permission_classes = [AllowAny]
    
    def post(self,request):
        query = request.data.get("query",None)
        if not query:
            return Response(status=status.HTTP_404_NOT_FOUND,data='No query to populate data')

        skills = Skill.objects.filter(title__icontains=query)

        if not skills.exists():
            return Response(status=status.HTTP_200_OK,data='no data')

        skills = SkillSerializer(skills,many=True).data

        return Response(status=status.HTTP_200_OK,data=skills)


class GetUserProfileBundle(generics.RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = DifferentUserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)
        

class GetNotficationCount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        count = Notification.objects.filter(user=request.user,is_read=False).count()
        return Response(status=status.HTTP_200_OK,data=count)