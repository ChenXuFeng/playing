'''
Date       :   2023-02
Author     :   ChenXuFeng <xu.sz@outlook.com> 
Describe   :   全局分页  
'''

from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    invalid_page_message = '无效页'
    page_size = 10
    max_page_size = 50
    page_query_param = 'pi'
    page_size_query_param = 'ps'
