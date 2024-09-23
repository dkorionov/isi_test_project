from threads.models import Message, Thread

from rest_framework import serializers


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ["id", "created_at", "updated_at", "participants", 'creator']
        read_only_fields = ("id", "created_at", "updated_at", "creator")


class ThreadQueryParamsSerializer(serializers.Serializer):
    participants = serializers.ListField(child=serializers.IntegerField(), required=True)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "thread", "sender", "content", "created_at", "updated_at"]


class MessageInputSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)
