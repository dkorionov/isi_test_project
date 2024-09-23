from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.filters import OrderingFilter
from rest_framework.validators import ValidationError

from threads.filters import ThreadFilter
from threads.models import Message, Thread
from threads.serializers import MessageInputSerializer, MessageSerializer, ThreadQueryParamsSerializer, ThreadSerializer
from threads.service import MessageService, ParticipantsError, ThreadService

__all__ = [
    "ListThreadAPI", "DeleteThreadAPi", "RetrieveOrCreateThreadAPI",
    "CreateListMessageAPI", "RetrieveMessageAPI", "RetrieveUnreadMessagesAPI"
]

"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3MTMxODczLCJpYXQiOjE3MjcxMjgyNzMsImp0aSI6IjE4NTAwNWY0NTM5NzRkOWM5MzZhN2RjMzc2ZTFlN2M1IiwidXNlcl9pZCI6MX0.YDzno06u6r2GoPK1eQh0lB8jgoJyID1OJWuSia2PQos"


class ListThreadAPI(generics.ListAPIView):
    serializer_class = ThreadSerializer
    queryset = Thread.objects.all().prefetch_related('participants')
    service = ThreadService
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ThreadFilter
    ordering_fields = ['created_at']

    @extend_schema(parameters=[
        OpenApiParameter(
            name='participants',
            required=True,
            type=list[int],
            location=OpenApiParameter.QUERY
        )])
    def get(self, request, *args, **kwargs):
        ThreadQueryParamsSerializer(data=request.query_params).is_valid(raise_exception=True)
        return super().get(request, *args, **kwargs)


class RetrieveOrCreateThreadAPI(generics.CreateAPIView):
    serializer_class = ThreadSerializer
    queryset = Thread.objects.all()
    service = ThreadService

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participants = serializer.validated_data['participants']
        thread = self.service.get_thread_by_participants(
            [participant.id for participant in participants]
        )
        if thread is None:
            try:
                thread = self.service.create_thread_with_participants(
                    creator_id=request.user.id,
                    participants=participants,
                )
            except ParticipantsError as e:
                raise ValidationError(e.message)
        response_data = ThreadSerializer(instance=thread).data
        return response.Response(response_data, status=status.HTTP_201_CREATED)


class DeleteThreadAPi(generics.DestroyAPIView):
    serializer_class = ThreadSerializer
    queryset = Thread.objects.all()

    def check_object_permissions(self, request, obj: Thread):
        if (
                request.user.id == obj.creator_id
                or request.user.id in obj.participants.values_list('id', flat=True)
        ):
            return
        self.permission_denied(request, message="You don't have permission to delete this thread", code=403)


class CreateListMessageAPI(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    service = MessageService()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    @extend_schema(responses=MessageSerializer)
    def get(self, request, pk: int, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(responses=MessageSerializer, request=MessageInputSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(thread_id=self.kwargs['pk'])

    def create(self, request, *args, **kwargs):
        serializer = MessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        threads_qs = Thread.objects.prefetch_related("participants")
        thread = get_object_or_404(threads_qs, id=kwargs['pk'])
        if not self.service.check_thread_message_permission(thread, request.user.id):
            return response.Response(
                {"detail": "You don't have permission to send messages to this thread"},
                status=status.HTTP_403_FORBIDDEN,
            )
        message = self.service.create_message(
            sender_id=request.user.id,
            content=data['content'],
            thread=thread,
        )
        response_data = MessageSerializer(instance=message).data
        return response.Response(response_data, status=status.HTTP_201_CREATED)


class RetrieveMessageAPI(generics.RetrieveAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    service = MessageService()

    @extend_schema(responses=MessageSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        message = super().get_object()
        self.service.mark_message_as_read(self.request.user.id, [message.id])
        return message


class RetrieveUnreadMessagesAPI(generics.ListAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all().prefetch_related('user_unread_messages', 'user_unread_messages__user')
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        return Message.objects.filter(
            user_unread_messages__user_id=self.request.user.id,
            user_unread_messages__is_read=False,
        )
