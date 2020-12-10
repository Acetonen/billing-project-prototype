from rest_framework import pagination


class TransactionsPagination(pagination.PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'