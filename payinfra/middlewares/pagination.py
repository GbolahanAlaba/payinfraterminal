import logging
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.request import Request

logger = logging.getLogger(__name__)


# Base reusable pagination with meta info
class AutoPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                    "page_size": self.get_page_size(self.request),
                },
                "results": data,
            }
        )


# Different pagination classes for different content types
class TrackPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class AlbumPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class ArtistPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class PostPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 40


class CommentPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class LikePagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = "page_size"
    max_page_size = 100


class FollowPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 80


class UserPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 60


class PlaylistPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class SmartAutoPaginationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.paginators = {
            "default": AutoPagination(),
            "track": TrackPagination(),
            "album": AlbumPagination(),
            "artist": ArtistPagination(),
            "post": PostPagination(),
            "comment": CommentPagination(),
            "like": LikePagination(),
            "follow": FollowPagination(),
            "user": UserPagination(),
            "playlist": PlaylistPagination(),
        }

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):
        logger.debug(f"Processing request: {request.path}")

        if (
            request.method == "GET"
            and hasattr(response, "data")
            and isinstance(response.data, list)
            and response.status_code in [200, 201]
            and not self._should_skip_pagination(request)
        ):
            logger.debug(
                f"Considering pagination for {request.path}, data length: {len(response.data)}"
            )

            if self._should_paginate(response, request):
                try:
                    paginator = self._get_paginator_for_request(request)
                    logger.debug(
                        f"Selected paginator: {paginator.__class__.__name__} for path: {request.path}"
                    )

                    # Prefer DRF Request if available
                    drf_request = getattr(response, "request", None)
                    if not isinstance(drf_request, Request):
                        drf_request = Request(request)

                    paginator.request = drf_request
                    page = paginator.paginate_queryset(response.data, drf_request)

                    if page is not None:
                        logger.debug(
                            f"Paginating response: {len(page)} items out of {len(response.data)}"
                        )
                        paginated_response = paginator.get_paginated_response(page)

                        # Preserve DRF rendering context
                        if hasattr(response, "accepted_renderer"):
                            paginated_response.accepted_renderer = response.accepted_renderer
                            paginated_response.accepted_media_type = response.accepted_media_type
                            paginated_response.renderer_context = response.renderer_context

                        paginated_response.request = drf_request
                        response = paginated_response
                    else:
                        logger.debug("Page is None, not paginating")
                except Exception as e:
                    logger.error(f"Pagination error for {request.path}: {e}")
        else:
            logger.debug(f"Skipping pagination for {request.path} - conditions not met")

        return response

    def _get_paginator_for_request(self, request):
        """Choose paginator based on URL path"""
        path = request.path
        if "/tracks/" in path:
            return self.paginators["track"]
        elif "/albums/" in path:
            return self.paginators["album"]
        elif "/artists/" in path:
            return self.paginators["artist"]
        elif "/posts/" in path:
            return self.paginators["post"]
        elif "/comments/" in path:
            return self.paginators["comment"]
        elif "/likes/" in path:
            return self.paginators["like"]
        elif "/follows/" in path:
            return self.paginators["follow"]
        elif "/users/" in path:
            return self.paginators["user"]
        elif "/playlists/" in path:
            return self.paginators["playlist"]
        return self.paginators["default"]

    def _should_skip_pagination(self, request):
        """Skip pagination for certain requests"""
        skip_params = ["no_pagination", "all", "export"]
        if any(param in request.GET for param in skip_params):
            return True

        skip_paths = [
            "/api/music/all/",
            "/admin/",
            "/swagger/",
            "/redoc/",
            "/api/auth/",
        ]
        return any(request.path.startswith(path) for path in skip_paths)

    def _should_paginate(self, response, request):
        """Decide if response should be paginated"""
        data = response.data

        # Already paginated
        if isinstance(data, dict) and "results" in data:
            return False

        # Skip small lists
        if not data or len(data) <= 5:
            return False

        # Explicit request
        if "page" in request.GET or "page_size" in request.GET:
            return True

        # Paginate larger lists
        default_size = self.paginators["default"].page_size
        return len(data) > default_size
