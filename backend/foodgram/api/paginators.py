from rest_framework.pagination import PageNumberPagination

from core.config import Constans


class PageLimitPagination(PageNumberPagination):
    """Стандартный пагинатор с определением атрибута
    `page_size_query_param`, для вывода запрошенного количества страниц.
    """
    page_size = Constans.PAGE_SIZE
    page_size_query_param = "limit"
