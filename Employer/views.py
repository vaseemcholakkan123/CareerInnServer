from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status,viewsets,generics,pagination
from .models import *
from .serializers import * 
from .mixins import *
from .signals import progress_signal
from User.views import NormalPagination
from User.models import Notification
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.

class ApplyValidation(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target_job = request.data.get('job_id',None)

        if not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no target id found')

        target_job = Job.objects.filter(id=target_job)

        if not target_job.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='no job for provided target id')

        target_job = target_job.first()

        if RejectedApplicant.objects.filter(user=request.user,job=target_job).exists():
            return Response(status=status.HTTP_200_OK,data={'not_valid' : "You can't apply for this job!"})


        if request.user.company == target_job.company:
            return Response(status=status.HTTP_200_OK,data={'not_valid' : "You are already working in this company!"})
        else:
            return Response(status=status.HTTP_200_OK,data={'valid':True})

class ApplyForJob(APIView):
    permission_classes = [IsAuthenticated]

    
    def post(self,request):
        target_job = request.data.get('job_id',None)
        answer_validation = request.data.get('answer_validation',None)
        resume = request.data.get('resume',None)
        about = request.data.get('about',None)

        if answer_validation == 'false':
            answer_validation = False
        else:
            answer_validation = True

        if not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no target id found')

        if answer_validation is None:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no answer validation found')
        
        if not resume and not request.user.is_premium_user and not request.user.resume:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no attached resume')
        
        if not resume and request.user.is_premium_user:
            resume = request.user.resume

        target_job = Job.objects.filter(id=target_job)\

        if not target_job.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='no job for provided target id')

        target_job = target_job.first()

        applicant = target_job.applicants.filter(user=request.user)

        if not answer_validation:
            RejectedApplicant.objects.create(user=request.user,job=target_job)
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data={'rejected':True})

        if applicant.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data={'applied':'You have already applied to this job'})
        else:
            applicant = Applicant.objects.create(user=request.user,resume=resume,about=about)
            progress_signal.send(sender=Applicant,instance=applicant,created=True,job_id=str(target_job.id),thread_img=target_job.company.logo.url,job_name=target_job.name)
            
            target_job.applicants.add(applicant)
            target_job.save()
            return Response(status=status.HTTP_200_OK,data={'success':True})

class GetJobApplicants(APIView):

    permission_classes = [AllowAny]

    def post(self,request):

        target = request.data.get('job_id',None)
        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No target id of job id')

        target = Job.objects.filter(id=target)

        if not target.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='No job for this id') 

        target = target.first()

        queryset = target.applicants.all()

        data = ApplicantSerializer(queryset,many=True).data

        return Response(status=status.HTTP_200_OK,data=data)

class ShortlistApplicant(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):

        target = request.data.get('applicant_id',None)
        target_job = request.data.get('job_id',None)

        if not target:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no target applicant id')

        if not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no job id found')

        target = Applicant.objects.filter(id=target)

        if not target.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='target applicant with this id not found')

        target = target.first()
        
        target_job = Job.objects.filter(id=target_job)

        if not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no job with this id')

        target_job = target_job.first()

        target.is_shortlisted = True
        target.save()
        progress_signal.send(sender=Applicant,instance=target,created=False,job_id=str(target_job.id),thread_img=target_job.company.logo.url,job_name=target_job.name)


        return Response(status=status.HTTP_200_OK,data='Shortlisted')
    
class RemoveApplicant(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):

        target = request.data.get('applicant_id',None)
        target_job = request.data.get('job_id',None)

        if not target or not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no data to populate result')

        target = Applicant.objects.filter(id=target)
        target_job = Job.objects.filter(id=target_job)

        if not target_job.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='No job found with this id')

        target_job = target_job.first()

        if not target.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='target applicant with this id not found')

        target = target.first()

        if not target_job.applicants.filter(id=target.id).exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED,data='Applicant is not valid')
        

        RejectedApplicant.objects.create(user=target.user,job=target_job)
        target.delete()

        return Response(status=status.HTTP_200_OK,data='Applicant Removed')


class UserJobs(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyJobSerializer
    pagination_class = NormalPagination
    


    def get_queryset(self):
      
        work_type = self.request.GET.get('work_type')
        work_time = self.request.GET.get('work_time')
        department = self.request.GET.get('department')
        skills = self.request.GET.get('skills')
        skills_arr = []
        self.queryset = Job.objects.filter(is_closed=False)

        # if not work_type and not work_time and not department and not skills:
        #     user_skills = self.request.user.skills.all()
        #     local_q = self.queryset.filter(skills_required__in=user_skills).distinct()
        #     print(local_q[0].name,'llllllllllll')

        #     print('disabled')
        #     self.queryset = self.queryset.exclude(pk__in=local_q)
        #     for s in self.queryset:
        #         print(s.name)

        #     print('final========')
        #     self.queryset = local_q | self.queryset.distinct()

        #     for s in self.queryset:
        #         print(s.name)
        #     # self.queryset = self.queryset.distinct()


        if work_type:
            self.queryset = self.queryset.filter(job_type=work_type)
        if work_time:
            self.queryset = self.queryset.filter(job_time=work_time)

        if skills:
            tmp = ''
            for id in skills:
                if id != "'" and id != ',':
                    tmp += id
                if id == ',':
                    skills_arr.append(int(tmp))
                    tmp = ''

            skills_arr.append(int(tmp))



            self.queryset = self.queryset.filter(skills_required__in=skills_arr).distinct()

        if department:
            department = Department.objects.filter(id=department)
            if department.exists():
                self.queryset = self.queryset.filter(company__department=department.first())

        return super().get_queryset()
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)

class CompanyJobs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        queryset = Job.objects.filter(company=request.user.company)
        jobs = CompanyJobSerializer(queryset,many=True).data
        return Response(status=status.HTTP_200_OK,data=jobs)
    
class SendInterviewNotification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        job_id = request.data.get("job_id",None)
        target_applicant = request.data.get("target_id",None)
        interview_time = request.data.get("interview_time",None)
        interview_date = request.data.get("interview_date",None)

        if not job_id:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No job id provided')

        if not interview_time or not interview_date:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No time or date provided')

        if not target_applicant:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No applicant id provided')

        target_job = Job.objects.filter(id=job_id)

        if not target_job.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Bad job id')

        target_job = target_job.first()

        target_applicant = Applicant.objects.filter(id=target_applicant)

        if not target_applicant.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Bad applicant id')
        target_applicant = target_applicant.first()
        target_applicant.interview_time = interview_time
        target_applicant.interview_date = interview_date
        target_applicant.is_informed = True
        target_applicant.save()

        progress_signal.send(sender=Applicant,instance=target_applicant,created=False,job_id=str(target_job.id),thread_img=target_job.company.logo.url,job_name=target_job.name)

        return Response(status=status.HTTP_200_OK)

class TakeInterview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        applicant = request.data.get('applicant',None)
        job = request.data.get('job',None)


        if not applicant:
            return Response(status.HTTP_400_BAD_REQUEST,data='no applicant id')
        
        if not job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='no job id')

        applicant = Applicant.objects.filter(user__id=applicant)
        job = Job.objects.filter(id=job).first()

        if not applicant.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Not Found')
        applicant = applicant.first()

        if not job.applicants.filter(user=applicant.user).exists():
            return Response(data='not a valid applicant id',status=status.HTTP_400_BAD_REQUEST)

        progress_signal.send(sender=Applicant,instance=applicant,created=False,job_id=str(job.id),thread_img=job.company.logo.url,job_name=job.name,starting_interview=True)

        subject = 'Join Interview'
        message = f'Your interview for the job has been started , please join as soon as possible, link is shared in the notifiaction.'
        email_from = settings.EMAIL_HOST
        send_mail(subject,message,email_from , [applicant.user.email])

        return Response(status=status.HTTP_200_OK)

class SetUserIsInterviewed(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.data.get('user_id',None)
        job = request.data.get('job_id',None) 

        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No user id')

        if not job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No job id')
        
        user = User.objects.filter(id=user)

        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Not a user with this id')
        
        job = Job.objects.filter(id=job)

        if not job.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No job with this id found')
        
        user = user.first()
        job = job.first()

        applicant = job.applicants.filter(user=user)

        if not applicant.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Not a valid applicant id')
        
        applicant = applicant.first()
        applicant.is_interviewed = True
        applicant.save()
        progress_signal.send(sender=Applicant,instance=applicant,created=False,job_id=str(job.id),thread_img=job.company.logo.url,job_name=job.name)

        return Response(status=status.HTTP_200_OK)

class SelectApplicant(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.data.get('user_id',None)
        job = request.data.get('job_id',None)

        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No user id')

        if not job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No job id')
        
        user = User.objects.filter(id=user)

        if not user.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Not a user with this id')
        
        job = Job.objects.filter(id=job)

        if not job.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No job with this id found')
        
        user = user.first()
        job = job.first()

        applicant = job.applicants.filter(user=user)

        if not applicant.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST,data='Not a valid applicant id')
        
        applicant = applicant.first()
        applicant.is_selected = True
        applicant.save()
        progress_signal.send(sender=Applicant,instance=applicant,created=False,job_id=str(job.id),thread_img=job.company.logo.url,job_name=job.name)

        return Response(status=status.HTTP_200_OK)


class RegisterCompany(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CreateCompanySerializer

    def perform_create(self, serializer):
        company = serializer.save()
        company.ceo.company = company
        company.ceo.save()  
    
class AddJob(JobMixin,generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = CreateJobSerializer

class UpdateJob(JobMixin,generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = CreateJobSerializer

class CompanyAction(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = Company.objects.all()
    serializer_class = CreateCompanySerializer

class CompanyBanner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        banner = request.data.get('banner')
        if not banner:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No embedded banner')
        request.user.company.banner.save(banner.name, banner, save=True)

        return Response(status=status.HTTP_200_OK,data={'new_banner':request.user.company.banner.url})

class CompanyLogo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        logo = request.data.get('logo')
        if not logo:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No embedded banner')
        request.user.company.logo.save(logo.name, logo, save=True)

        return Response(status=status.HTTP_200_OK,data={'new_logo':request.user.company.logo.url})

class GetRecruiters(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        users = User.objects.filter(company=self.request.user.company)
        users = UserSerializer(users,many=True).data
        return Response(status=status.HTTP_200_OK,data=users)
    
class RemoveRecruiter(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        company = self.request.user.company
        target_user = request.data.get("target",None)

        if not target_user:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No query to populate')

        target_user = User.objects.filter(id=target_user)
        if target_user.exists():
            target_user = target_user.first()

            if not target_user.company == company:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            target_user.company = None
            target_user.save()
            return Response(status=status.HTTP_202_ACCEPTED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No such user')

class CloseJob(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        target_job = request.data.get('target',None)
        if not target_job:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No target provided')
        
        target_job = Job.objects.filter(id=target_job)

        if not target_job.exists():
            return Response(status=status.HTTP_404_NOT_FOUND,data='Job with that id is not found')

        target_job = target_job.first()

        if not request.user.company == target_job.company:
            return Response(status=status.HTTP_401_UNAUTHORIZED,data='Unauthorized')

        target_job.is_closed = True
        target_job.save()
        return Response(status=status.HTTP_200_OK,data='success')


class AddNewRecruiter(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        company = self.request.user.company
        target_user = request.data.get("target",None)

        if not target_user:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No query to populate')

        target_user = User.objects.filter(id=target_user)

        if target_user.exists():
            target_user = target_user.first()

            if target_user.company and target_user.company == company:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data='User already Recruiter in the company') 

            if target_user.company:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE,data='User is Recruiter in another company')

            target_user.company = company
            target_user.save()
            target_user = UserSerializer(target_user,many=False).data
            return Response(status=status.HTTP_202_ACCEPTED,data=target_user)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No such user')


class SearchDepartment(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        query = request.data.get("query",None)
        if not query:
            return Response(status=status.HTTP_404_NOT_FOUND,data='No query to populate data')

        departments = Department.objects.filter(title__icontains=query)

        if not departments.exists():
            return Response(status=status.HTTP_200_OK,data='no data')

        departments = DepartmentSerializer(departments,many=True).data

        return Response(status=status.HTTP_200_OK,data=departments)
    
class SearchCompany(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        query = request.data.get("query",None)
        if not query:
            return Response(status=status.HTTP_404_NOT_FOUND,data='No query to populate data')

        companies = Company.objects.filter(name__icontains=query)

        if not companies.exists():
            return Response(status=status.HTTP_200_OK,data='no data')

        companies = CompanySerializer(companies,many=True).data

        return Response(status=status.HTTP_200_OK,data=companies)

class RetrieveJob(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    serializer_class = CompanyJobSerializer
    queryset = Job.objects.all()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context'] = {'request':self.request}
        return serializer_class(*args, **kwargs)
