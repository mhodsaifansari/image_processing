import json
from rest_framework.serializers import Serializer, FileField, ModelSerializer,SerializerMethodField,ValidationError

from image_processing.models import ProcessingRequest, Setting

class UploadSerializer(Serializer):
    file = FileField()
    class Meta:
        fields = ['file']
    

class ProcessingRequestNotCompleted(ModelSerializer):
    class Meta:
        model = ProcessingRequest
        fields=['id','status','created_at']


class ProcessingRequestFailed(ModelSerializer):
    class Meta:
        model = ProcessingRequest
        fields=['id','status','created_at','completed_at','failure_reason']

class ProcessingRequestFailedWebhook(ModelSerializer):
    webhook = SerializerMethodField()
    def get_webhook(self,obj):
        return {
            'status':obj['webhook_status'],
            'request':obj['webhook_request'],
            'response':obj['webhook_response'],
            'webhook_url':obj.webhook_setting.url
        }
    class Meta:
        model = ProcessingRequest
        fields=['id','status','created_at','completed_at','failure_reason','webhook']

class ProcessingRequestCompleted(ModelSerializer):
    csv_file = SerializerMethodField()
    
    def get_csv_file(self, obj):
        if self.context['csv_file']:
            return self.context['csv_file']
        else:
            raise ValidationError('csv_file not provided')
    
    class Meta:
        model = ProcessingRequest
        fields=['id','status','created_at','completed_at','csv_file']

class ProcessingRequestCompletedWithWebhook(ModelSerializer):
    csv_file = SerializerMethodField()
    webhook = SerializerMethodField()
    def get_csv_file(self, obj):
        if self.context['csv_file']:
            return self.context['csv_file']
        else:
            raise ValidationError('csv_file not provided')
        
    def get_webhook(self,obj):
        return {
            'status':obj.webhook_status,
            'request':json.loads(obj.webhook_request),
            'response':json.loads(obj.webhook_response),
            # 'webhook_url':obj.webhook_setting.url
        }
    class Meta:
        model = ProcessingRequest
        fields=['id','status','created_at','completed_at','csv_file','webhook']


class SettingSerializer(ModelSerializer):
    class Meta:
        model = Setting
        fields = ['url']