from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import register_user, login_user, logout_user , request_reset_email, reset_password, list_menus,create_menu,delete_menu,update_menu , check_votes, submit_vote , report_view, menu_vote_count, check_report_status,download_report
urlpatterns = [
    path('', register_user, name='register'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout'),
    path('password-reset/', request_reset_email, name='password-reset'),
    path('reset-password/<uid>/<token>/', reset_password, name='reset-password'),
    path('menus/', list_menus, name='list_menus'),
    path('menus/create/', create_menu, name='create_menu'),
    path('edit/menus/<int:menu_id>/', update_menu, name='update_menu'),
    path('menus/<int:menu_id>/', delete_menu, name='delete_menu'),
    path('menus/<int:id>/votes/', menu_vote_count, name='menu-vote-count'),
    path('votes/', submit_vote, name='submit-vote'),
    path('votes/list', check_votes, name='check-votes'),
    path('report/' , report_view, name='report_view'),
    path ('status/', check_report_status, name='report_status'),
   path('download-report/', download_report, name='download_report')

]