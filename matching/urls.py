from django.urls import path
from . import views
from matching.views import UserView, MatchingInfoView, MatchingResultView

urlpatterns = [
    path('users', UserView.as_view()),
    path('users/<int:id>', UserView.as_view()),
    path('infos', MatchingInfoView.as_view()),
    path('infos/<int:uid>', MatchingInfoView.as_view()),
    path('results', MatchingResultView.as_view()),
    path('results/<int:uid>', MatchingResultView.as_view())
]