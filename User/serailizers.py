from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser 
from .models import *

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username","email", "password")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
    
class AdminUserSerializer(serializers.ModelSerializer):
    posts_got_reported = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id","username","info", "posts_got_reported" , "is_blocked" , 'profile')

    def get_posts_got_reported(self,usr):
        if isinstance(usr,AnonymousUser):
            return 0

        return Report.objects.filter(post__posted_user=usr).count()
        


class UserSerializer(serializers.ModelSerializer):
    is_ceo = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id','username','info','profile','is_ceo','date_joined')

    def get_is_ceo(self,usr):

        if isinstance(usr,AnonymousUser):
            return False

        if not usr.company:
            return False
        company = usr.company

        if company.ceo == usr:
            return True
        else:
            return False
        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

        
class DifferentUserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True , read_only=True)
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ('id','username','info','profile','date_joined' , 'is_following' ,'banner' , 'location' , 'skills' , 'education' , 'experience' , 'projects' )

    def get_education(self,usr):
        return EducationSerializer(Education.objects.filter(user=usr),many=True).data
    
    def get_experience(self,usr):
        return RetrieveExpSerializer(Experience.objects.filter(user=usr),many=True).data

    def get_projects(self,usr):
        return RetrieveProjectSerializer(Project.objects.filter(user=usr),many=True).data
    
    def get_is_following(self,usr):
        fetch_user = self.context['request'].user
        connection_obj = connections.objects.filter(user=fetch_user,following=usr)
        if not connection_obj.exists():
            return False
        else: return True




class postsSeriallizer(serializers.ModelSerializer):
    posted_user = UserSerializer(read_only=True,many=False)
    is_liked = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_is_liked(self,obj):
        user = self.context['request'].user
        if isinstance(user,AnonymousUser):
            return False
        like_obj = Like.objects.filter(user=user,post=obj)
        if not like_obj.exists():
            return False
        return like_obj.first().liked
    
    def get_is_following(self,obj):
        user = self.context['request'].user
        if isinstance(user,AnonymousUser):
            return False
        connection_obj = connections.objects.filter(user=user,following=obj.posted_user)
        if not connection_obj.exists():
            return False
        else: return True

    def get_is_saved(self,obj):
        user = self.context['request'].user
        if isinstance(user,AnonymousUser):
            return False
        if SavedPosts.objects.filter(user=user,post=obj).exists():
            return True
        else:
            return False

class SavedPostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavedPosts
        fields = ('post',)

    def to_representation(self, instance):
        # Flatten the list of posts and return them directly
        return list(instance.post.all().values())



        
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields= '__all__'

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields= '__all__'

class RetrieveExpSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    class Meta:
        model = Experience
        fields= '__all__'

    def get_company(self, obj):
        from Employer.serializers import CompanySerializer
        company_obj = obj.company  
        serializer = CompanySerializer(instance=company_obj)
        return serializer.data


class commentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many = False,read_only = True)
    class Meta:
        model = comment
        fields = ('user','comment_text','commented_on')

class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False,read_only=True)
    class Meta:
        model = connections
        fields = ('user',)

class FollowingSerializer(serializers.ModelSerializer):
    following = UserSerializer(many=True,read_only=True)
    class Meta:
        model = connections
        fields = ('following',)


class CreateProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'

class RetrieveProjectSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    class Meta:
        model = Project
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class CreateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    post = postsSeriallizer(many=False)
    user = UserSerializer(many=False)
    total_reports = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'

    def get_total_reports(self,obj):
        reports = Report.objects.filter(post=obj.post)
        return reports.count()