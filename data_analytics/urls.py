from django.urls import path
from . import views

urlpatterns = [
    path("",views.home,name = 'home'),
    path("post_data", views.post_data, name = 'post_data'),
    path('show/<int:id>',views.show,name="show"),
    path('data_analysis', views.data_analysis, name = 'data_analysis'),
    path('download', views.download, name = 'download'),
    path('send_email', views.send_email, name = 'send_email')
]