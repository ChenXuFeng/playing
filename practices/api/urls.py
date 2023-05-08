'''
Date       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from django.urls import path

from ..views import DockerImagesLC, DockerImagesList, DockerImagesRUD

urlpatterns = [
    path('register/dockerimage', DockerImagesLC.as_view()),
    path('dockerimage/<int:pk>', DockerImagesRUD.as_view()),
    path('dockerimage/all', DockerImagesList.as_view())
]