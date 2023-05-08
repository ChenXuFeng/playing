'''
Time       :   2023-03
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   
'''


from django.urls import path

from ..views import (AnswerCreate, AnswerDel, AnswersUpdate, AnswerUpdate,
                     ClasfLC, ClasRUD, QsAttrCreateView, QsAttrDelView,
                     QsAttrRetrieveView, QuestionAttaches, QuestionLC,
                     QuestionRUD, StartContainer, StopContainer)

urlpatterns = [
    path('questions', QuestionLC.as_view()),
    path('questions/<int:pk>', QuestionRUD.as_view()),
    path('question/attr', QsAttrCreateView.as_view()),
    path('question/attr/file/<str:fid>', QuestionAttaches.as_view()),
    path('question/attr/list/<int:pk>', QsAttrRetrieveView.as_view()),
    path('question/attr/<str:uuid>', QsAttrDelView.as_view()),
    path('question/start/container', StartContainer.as_view()),
    path('question/stop/container', StopContainer.as_view()),
    path('question/class', ClasfLC.as_view()),
    path('question/class/<int:pk>', ClasRUD.as_view()),
    path('question/update/answers/<int:pk>', AnswersUpdate.as_view()),
    path('question/update/answer/<int:pk>', AnswerUpdate.as_view()),
    path('question/answer', AnswerCreate.as_view()),
    path('question/answer/<int:pk>', AnswerDel.as_view())
]
