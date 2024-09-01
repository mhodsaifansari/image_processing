import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Setting(models.Model):
    id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()

# Create your models here.
class ProcessingRequest(models.Model):
    class ProcessingStatus(models.TextChoices):
        PENDING = "pending",_("pending")
        IN_PROGESS = "in_progess",_("in_progess")
        SUCCESS = "success",_("success")
        FAILED = "failed",_("failed")

    class WebhookStatus(models.TextChoices):
        NOT_SENT = "not_sent",_("not_sent")
        SENT = "sent",_("sent")

    id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=30,choices=ProcessingStatus.choices,default=ProcessingStatus.IN_PROGESS)
    webhook_status = models.CharField(max_length=30,choices=WebhookStatus.choices,null=True)
    webhook_request = models.TextField(null=True,blank=True)
    webhook_response = models.TextField(null=True,blank=True)
    webhook_setting = models.ForeignKey(to=Setting,null=True,blank=True,on_delete=models.DO_NOTHING)
    failure_reason = models.TextField(null=True)
    image_count = models.PositiveIntegerField(null=True)

class SKUItem(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.TextField()
    request = models.ForeignKey(to=ProcessingRequest,on_delete=models.CASCADE)


class Images(models.Model):
    class ImageType(models.TextChoices):
        input = "input",_("input")
        processed = "proccessed",_("input")
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.ForeignKey(to=SKUItem,on_delete=models.CASCADE)
    type = models.CharField(max_length=30,choices=ImageType.choices)
    image = models.ImageField(upload_to='images',null=True) 
    image_url=models.URLField(null=True) 


