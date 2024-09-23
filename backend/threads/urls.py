from django.urls import include, path

from threads.views import CreateListMessageAPI, ListThreadAPI, DeleteThreadAPi, RetrieveOrCreateThreadAPI, \
    RetrieveUnreadMessagesAPI, RetrieveMessageAPI

app_name = "threads"
urlpatterns = [
    path("", ListThreadAPI.as_view(), name="thread-list"),
    path("create-retrieve/", RetrieveOrCreateThreadAPI.as_view(), name="thread-create-retrieve"),
    path("<int:pk>/", DeleteThreadAPi.as_view(), name="thread-delete"),
    path("<int:pk>/messages/", CreateListMessageAPI.as_view(), name="create-list-message"),
    path("messages/", include([
        path("<int:pk>/", RetrieveMessageAPI.as_view(), name="retrieve-message"),
        path("unread/", RetrieveUnreadMessagesAPI.as_view(), name="retrieve-unread-messages")
    ]))

]
