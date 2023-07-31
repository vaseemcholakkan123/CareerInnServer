from django.urls import path
from . import views

urlpatterns = [
    path('register-company/',views.RegisterCompany.as_view(),name='register-company'),
    path('company-action/<int:pk>/',views.CompanyAction.as_view(),name='company-action'),
    path('update-company-banner/',views.CompanyBanner.as_view(),name='update-company-banner'),
    path('update-company-logo/',views.CompanyLogo.as_view(),name='update-company-logo'),


    path('search/',views.SearchDepartment.as_view(),name='search-department'),
    path('search-company/',views.SearchCompany.as_view(),name='search-company'),
    path('get-recruiters/',views.GetRecruiters.as_view(),name='get-company-recruiters'),
    path('add-new/',views.AddNewRecruiter.as_view(),name='add-new-recruiter'),
    path('remove-recruiter/',views.RemoveRecruiter.as_view(),name='remove-recruiter'),
    path('get-company-jobs/',views.CompanyJobs.as_view(),name='get-company-jobs'),
    path('add-job/',views.AddJob.as_view(),name='add-company-job'),
    path('update-job/<int:pk>',views.UpdateJob.as_view(),name='update-job'),
    path('close-job/',views.CloseJob.as_view(),name='close-company-job'),
    path('get-job-applicants/',views.GetJobApplicants.as_view(),name='get-job-applicants'),
    path('remove-applicant/',views.RemoveApplicant.as_view(),name='remove-applicant'),
    path('shortlist-applicant/',views.ShortlistApplicant.as_view(),name='shortlist-applicant'),
    path('notify-interview/',views.SendInterviewNotification.as_view(),name='send-interview-notification'),

    path('user-jobs/',views.UserJobs.as_view(),name='jobs-for-user'),
    path('validate-user/',views.ApplyValidation.as_view(),name='validate_application'),
    path('apply-job/',views.ApplyForJob.as_view(),name='apply-for-job'),
    path('view-job/<int:pk>/',views.RetrieveJob.as_view(),name='retrieve-job'),
    path('take-interview/',views.TakeInterview.as_view(),name='take-interview'),
    path('is-interviewed/',views.SetUserIsInterviewed.as_view(),name='is-interviewed'),
    path('select-candidate/',views.SelectApplicant.as_view(),name='is-interviewed'),

]

