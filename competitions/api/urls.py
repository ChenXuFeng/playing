'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''

from django.urls import path

from ..views import (AnswerRecordLC, CompetitionGroups, CompetitionLC,
                     CompetitionQuestions, CompetitionRUD, Entry,
                     EntryResource, WPDownload, WriteUpLC)

urlpatterns = [
    path('competitions', CompetitionLC.as_view()),
    path('competition/<int:pk>', CompetitionRUD.as_view()),
    path('competition/group/answer/records', AnswerRecordLC.as_view()),
    path('competition/questions', CompetitionQuestions.as_view()),
    path('competition/groups', CompetitionGroups.as_view()),
    path('competition/entry', Entry.as_view()),
    path('competition/entry/resource/<str:types>', EntryResource.as_view()),
    path('competition/wp', WriteUpLC.as_view()),
    path('competition/wp/file/<str:fid>', WPDownload.as_view())
]