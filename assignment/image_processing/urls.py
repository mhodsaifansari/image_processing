

from django.urls import path

from . import views

urlpatterns = [
    path("health", views.Health.as_view(), name="index"),
    path("upload",views.UploadRequest.as_view(),name="upload"),
    path("status/<str:id>",views.GetRequest.as_view(),name='status'),
    path("csv/<str:id>",views.GetCSV.as_view(),name="Get_CSV"),
    path("setting",views.SetWebhook.as_view(),name='setting'),
    path("webhook",views.Webhook.as_view(),name="webhook")
]