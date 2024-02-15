from rest_framework.pagination import PageNumberPagination

from foodgram_backend.settings import PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Кастомная пагинация с параметром limit."""
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
