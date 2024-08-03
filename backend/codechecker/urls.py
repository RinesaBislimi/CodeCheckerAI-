from django.urls import path
from .views import CodeCheckView , GithubRepoAnalysisView , DatasetCheckView

urlpatterns = [
    path('check/', CodeCheckView.as_view(), name='code-check'),
    path('check-repo/', GithubRepoAnalysisView.as_view(), name='check-repo'),
    path('check-dataset/', DatasetCheckView.as_view(), name='check-dataset'),


]