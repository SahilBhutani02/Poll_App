from rest_framework import serializers
from .models import PollModel

class PollSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = PollModel
        fields = [
            'id', 'question',
            'option_one', 'option_two', 'option_three',
            'option_one_count', 'option_two_count', 'option_three_count',
            'total_votes', 'created_by'
        ]

    def get_total_votes(self, obj):
        return obj.total()

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None
