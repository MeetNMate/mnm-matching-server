from django.urls import path, include
from . import views
from rest_framework import routers
from matching.views import MatchingInfoViewSet, MatchingResultView

router = routers.DefaultRouter()
router.register('info', MatchingInfoViewSet)

urlpatterns = [
    path('', views.index),
    path('api/', include(router.urls)),
    path('result/', MatchingResultView.as_view()),
    path('result/<int:uid>', MatchingResultView.as_view()),
    path('matching_result/', views.matching_result),
]