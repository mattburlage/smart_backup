from django.urls import path

from backup import views

urlpatterns = [
    path("", views.index, name="index"),
    path("campaign/<int:camp_id>", views.campaign, name="campaign"),
    path("campaign/<int:camp_id>/initiate", views.initiate, name="initiate"),
    path("backup/<int:bac_id>/keep", views.keep_safe_toggle, name="toggle_keep"),
]
