from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('News',views.NewsAction,basename='news-action')
router.register('Department',views.DepartmentAction,basename='department-action')


urlpatterns = [
    path('check-auth/',views.CheckAuth.as_view()),
    path('login/',views.AdminLogin.as_view()),
    path('reports/',views.ReportsView.as_view()),
    path('delete-post/<post_id>/',views.DeletePost.as_view()),
    path('block-user/<user_id>/',views.BlockUser.as_view()),
    path('block-user-list/<user_id>/',views.BlockUserFromList.as_view()),
    path('unblock-user-list/<user_id>/',views.UnblockUserFromList.as_view()),
    path('users/',views.RetrieveUsers.as_view()),
]

urlpatterns = urlpatterns + router.urls