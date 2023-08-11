from rest_framework.response import Response
from rest_framework import status
from .models import JobRequirements,JobResponsibilities,JobQuestions
from User.models import Skill

class JobMixin:

    def post(self, request, *args, **kwargs):
        data = request.data

        reqs = data.get('requirements',None)
        respo = data.get('responsibilities',None)
        # skills = data.get('skills_required',None)
        ques = data.get('questions',None)


        if not respo:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Responsibilities specified') 
        if not reqs:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Requirements specified')
        # if not skills:
        #     return Response(status=status.HTTP_400_BAD_REQUEST,data='No Required skills specified')  
        if not ques:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Screening questions')  


        if respo:
            for idx,r in enumerate(respo):
                temp = JobResponsibilities.objects.filter(name=r)
                if temp.exists():
                    temp = temp.first()
                    respo[idx] = temp.id
                else:
                    temp = JobResponsibilities.objects.create(name=r)
                    respo[idx] = temp.id

        # if skills:
        #     for idx,r in enumerate(respo):
        #         temp = Skill.objects.filter(title=r)
        #         if temp.exists():
        #             temp = temp.first()
        #             skills[idx] = temp.id
        #         else:
        #             temp = Skill.objects.create(title=r)
        #             skills[idx] = temp.id

        if reqs:
            for idx,r in enumerate(reqs):
                temp = JobRequirements.objects.filter(name=r)
                if temp.exists():
                    temp = temp.first()
                    reqs[idx] = temp.id
                else:
                    temp = JobRequirements.objects.create(name=r)
                    reqs[idx] = temp.id

        if ques:
            for idx,r in enumerate(ques):
                temp = JobQuestions.objects.filter(name=r['name'])
                if temp.exists():
                    temp = temp.first()
                    ques[idx] = temp.id
                else:
                    temp = JobQuestions.objects.create(name=r['name'],answer_is_yes=r['answer_is_yes'])
                    ques[idx] = temp.id

        request.data['responsibilities'] = respo
        request.data['requirements'] = reqs
        # request.data['skills_required'] = skills
        request.data['questions'] = ques
        request.data['company'] = request.user.company.id


        return self.create(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        data = request.data

        reqs = data.get('requirements',None)
        respo = data.get('responsibilities',None)
        # skills = data.get('skills_required',None)
        ques = data.get('questions',None)


        if not respo:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Responsibilities specified') 
        if not reqs:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Requirements specified')
        # if not skills:
        #     return Response(status=status.HTTP_400_BAD_REQUEST,data='No Required skills specified')  
        if not ques:
            return Response(status=status.HTTP_400_BAD_REQUEST,data='No Screening questions')  


        if respo:
            for idx,r in enumerate(respo):
                temp = JobResponsibilities.objects.filter(name=r)
                if temp.exists():
                    temp = temp.first()
                    respo[idx] = temp.id
                else:
                    temp = JobResponsibilities.objects.create(name=r)
                    respo[idx] = temp.id

        # if skills:
        #     for idx,r in enumerate(respo):
        #         temp = Skill.objects.filter(title=r)
        #         if temp.exists():
        #             temp = temp.first()
        #             skills[idx] = temp.id
        #         else:
        #             temp = Skill.objects.create(title=r)
        #             skills[idx] = temp.id

        if reqs:
            for idx,r in enumerate(reqs):
                temp = JobRequirements.objects.filter(name=r)
                if temp.exists():
                    temp = temp.first()
                    reqs[idx] = temp.id
                else:
                    temp = JobRequirements.objects.create(name=r)
                    reqs[idx] = temp.id

        if ques:
            for idx,r in enumerate(ques):
                temp = JobQuestions.objects.filter(name=r['name'])
                if temp.exists():
                    temp = temp.first()
                    ques[idx] = temp.id
                else:
                    temp = JobQuestions.objects.create(name=r['name'],answer_is_yes=r['answer_is_yes'])
                    ques[idx] = temp.id

        request.data['responsibilities'] = respo
        request.data['requirements'] = reqs
        # request.data['skills_required'] = skills
        request.data['questions'] = ques
        request.data['company'] = request.user.company.id

        return self.update(request, *args, **kwargs)
