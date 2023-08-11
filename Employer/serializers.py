from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser 
from .models import *
from User.serailizers import UserSerializer,SkillSerializer


class CreateCompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Company
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    ceo = UserSerializer(read_only=True,many=False)
    department = DepartmentSerializer(read_only=True,many=False)

    class Meta:
        model = Company
        fields = '__all__'

class CreateJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__' 

class JobRequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequirements
        fields = '__all__'

class JobResponsibilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobResponsibilities
        fields = '__all__'

class JobQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobQuestions
        fields = '__all__'

class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False,read_only=True)
    class Meta:
        model = Applicant
        fields = '__all__'

class CompanyJobSerializer(serializers.ModelSerializer):
    questions = JobQuestionsSerializer(many=True,read_only=True)
    skills_required = SkillSerializer(many=True,read_only=True)
    requirements = JobRequirementsSerializer(many=True,read_only=True)
    responsibilities = JobResponsibilitiesSerializer(many=True,read_only=True)
    company = CompanySerializer(many=False,read_only=True)
    applicants_count = serializers.SerializerMethodField()
    interview_count = serializers.SerializerMethodField()
    user_is_applied = serializers.SerializerMethodField()


    class Meta:
        model = Job
        fields = '__all__'

    def get_applicants_count(self,obj):
        return obj.applicants.count()
    
    def get_interview_count(self,obj):
        return obj.applicants.filter(is_interviewed=True).count()

    def get_user_is_applied(self,obj):

        if not self.context.get('request',None):
            return False
        
        user = self.context['request'].user
        if isinstance(user,AnonymousUser):
            return False
        
        if obj.applicants.filter(user=user).exists():
            return True
        else:
            return False
        

class UserJobserializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False,read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('company','name','description','progress','id')

    def get_progress(self,obj):
        if not self.context.get('request',None):
            return False
        
        user = self.context['request'].user
        if isinstance(user,AnonymousUser):
            return False
        
        if RejectedApplicant.objects.filter(job=obj,user=user).exists():
                return "Application Rejected"
        
        applicant = obj.applicants.filter(user=user)
        if applicant.exists():
            applicant = applicant.first()

            if applicant.is_shortlisted and not applicant.is_interviewed and not applicant.is_informed and not applicant.is_selected:
                return "Application Shortlisted"
            if applicant.is_informed and not applicant.is_interviewed and not applicant.is_selected:
                return "Interview Informed"
            if applicant.is_interviewed and not applicant.is_selected:
                return "Interview result pending"
            if applicant.is_selected:
                return "Selected for job"
            else:
                return "Application pending"
        else:
            return "No applicaction found"
        
