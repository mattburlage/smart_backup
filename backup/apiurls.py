from django.urls import path

from backup import apiviews

urlpatterns = [
    path("initiate/<int:camp_id>", apiviews.initiate_backup, name="api_initiate"),
    path("keep/<int:bac_id>", apiviews.keep_safe_toggle, name="api_keep_toggle"),
    path("keep/", apiviews.keep_safe_toggle, name="api_keep_toggle_link"),
]
