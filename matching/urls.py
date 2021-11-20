from django.urls import path, include
from . import views
from matching.views import MatchingInfoView, MatchingResultView

urlpatterns = [
    path('infos', MatchingInfoView.as_view()),
    path('infos/<int:uid>', MatchingInfoView.as_view()),
    path('results', MatchingResultView.as_view()),
    path('results/<int:uid>', MatchingResultView.as_view()),
    path('matching_result/', views.matching_result),
]