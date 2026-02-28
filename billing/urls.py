# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register(r'tracks', views.MusicTrackViewSet, basename='music-track')
# router.register(r'albums', views.MusicAlbumViewSet, basename='music-album')
# router.register(r'artists', views.MusicArtistViewSet, basename='music-artist')
# router.register(r'genres', views.MusicGenreViewSet, basename='music-genre')
# router.register(r'playlists', views.MusicPlaylistViewSet, basename='music-playlist')
# router.register(r'track-plays', views.TrackPlayViewSet, basename='track-play')
# router.register(r'likes', views.LikeViewSet, basename='like')
# router.register(r'comments', views.CommentViewSet, basename='comment')
# router.register(r'posts', views.MusicPostViewSet, basename='music-post')


urlpatterns = [
    # path('', include(router.urls)),
    # path('all/', views.AllMusicView.as_view(), name='all-music'),
    # path('featured-tracks/', views.MusicTrackViewSet.as_view({'get': 'featured'}), name='featured-tracks'),
    # path('popular-tracks/', views.MusicTrackViewSet.as_view({'get': 'popular'}), name='popular-tracks'),
    # path('latest-tracks/', views.MusicTrackViewSet.as_view({'get': 'latest'}), name='latest-tracks'),
    # path('latest-post/', views.MusicPostViewSet.as_view({'get': 'latest'}), name='latest-posts'),
    # path('featured-posts/', views.MusicPostViewSet.as_view({'get': 'featured'}), name='featured-posts'),
]