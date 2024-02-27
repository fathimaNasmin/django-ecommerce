"""Custom Pagination for store api."""

from rest_framework import pagination

class CustomPagination(pagination.LimitOffsetPagination):
    """Custom pagination from parent limit and offset."""
    default_limit = 5
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 20
    
    