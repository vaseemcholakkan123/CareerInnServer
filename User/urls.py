from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('posts',views.PostsView,basename='posts_viewsset')



urlpatterns = [
    #  Auth urls

    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("create-user/", views.CreateUser.as_view(), name="create_user"),
    path("login/", views.UserLogin.as_view(), name="login"),
    path('verify-username-email/',views.Validate_Username_Email.as_view(),name='validate_username'),
    path('verify-otp/',views.VerifyOtp.as_view(),name='verify-otp'),
    path('get-new-otp/',views.GetNewOtp.as_view(),name='new-otp'),

    # User Action 

    path('change-profile-picture/',views.ChangeProfilePicture.as_view(),name='change-profile-picture'),
    path('change-banner-picture/',views.ChangeProfileBanner.as_view(),name='change-banner-picture'),
    path('change-details/',views.ChangeDetails.as_view(),name='change_details'),
    path('follow-user/',views.FollowUser.as_view(),name='follow-user'),
    path('break-connection/',views.BreakFollowingUser.as_view(),name='break-connection'),
    path('get-follower-list/',views.UserFollowers.as_view(),name='user-followers'),
    path('get-following-list/',views.FollowingUsers.as_view(),name='user-following'),
    path('add-project/',views.AddProject.as_view(),name='add-project'),
    path('retrieve-self-projects/',views.RetrieveProject.as_view(),name='retrieve-self-projects'),
    path('update-delete-project/<int:pk>/',views.UpdateProject.as_view(),name='update-delete-project'),
    path('get-posts/',views.GetUserPosts.as_view(),name='get-user-posts'),
    path('get-applied-jobs/',views.RetrieveUserJobs.as_view(),name='retrieve-user-jobs'),
    path('get-notifications/',views.RetrieveNotifications.as_view(),name='retireive-notification'),
    path('read-notification/',views.ReadNotification.as_view(),name='read-notification'),
    path('get-read-notifications/',views.RetrieveReadNotifications.as_view(),name='retireive-notification'),
    path('delete-notification/',views.DeleteNotification.as_view(),name='delete-notification'),
    path('mark-all-as-read/',views.MarkALLAsRead.as_view(),name='mark-all-as-read'),
    path('view-post/<int:pk>/',views.RetrieveDifferPost.as_view(),name='retrieve-post'),
    path('report-post/',views.ReportPost.as_view(),name='report-post'),
    path('saveUnsave-Post/',views.SaveUnsavePost.as_view(),name='save-unsave-post'),
    path('get-otp-for-reset/',views.GetForReset.as_view(),name='get-reset-otp'),
    path('change-password/',views.ChangePassword.as_view(),name='change-password'),

    #  Post urls

    path('like-post/<post_id>',views.LikePost.as_view(),name='like_post'),
    path('comment-on-post/<post_id>',views.AddComment.as_view(),name='post_comment'),
    path('delete-comment/<comment_id>',views.DeleteComment.as_view(),name='delete_comment'),
    path('post-comments/<post_id>',views.GetPostComments.as_view(),name='get_post_comments'),
    path('get-saved-posts/',views.GetSavedPosts.as_view(),name='get_saved_posts'),

    # other urls
    path('search/',views.SearchUser.as_view(),name='search-user'),
    path('search-skills/',views.SearchSkills.as_view(),name='search-skills'),
    path('create-skill/',views.CreateSkills.as_view(),name='create-skill'),
    path('check-company/',views.CheckCompanyRelation.as_view(),name='check-company'),
    path('get-company-details/',views.GetCompany.as_view(),name='get-company'),
    path('add-skill/',views.AddUserSkill.as_view(),name='add-skill'),
    path('remove-skill/',views.RemoveUserSkill.as_view(),name='remove-skill'),
    path('retrieve-skills/',views.RetrieveUserSkills.as_view(),name='retrieve-user-skills'),
    path('get-user-bundle/<int:pk>/',views.GetUserProfileBundle.as_view(),name='get-user-bundle'),
    path('get-different-user-posts/<user_id>/',views.GetDifferentUserPosts.as_view(),name='get-different-user-posts'),
    path('people-knows/',views.PeopleKnow.as_view(),name='people-u-know'),

    # Education and Experience

    path('add-education/',views.AddEducation.as_view(),name='Add-Education'),
    path('get-education/',views.RetrieveUserEducation.as_view(),name='user-education'),
    path('update-delete-education/<int:pk>/',views.UpdateEducation.as_view(),name='update-destroy-education'),

    path('add-experience/',views.AddExperience.as_view(),name='Add-experience'),
    path('get-experience/',views.RetrieveUserExperence.as_view(),name='user-experience'),
    path('update-delete-experience/<int:pk>/',views.UpdateExperience.as_view(),name='update-destroy-experience')

]   


urlpatterns = urlpatterns + router.urls