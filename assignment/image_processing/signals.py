
import datetime
from image_processing.tasks import webhook, work_image
from image_processing.service import Service
from image_processing.models import Images, ProcessingRequest
# from image_processing.service import Service
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
@receiver(post_save, sender=Images, weak=False)
def start_worker(sender,instance,**kwargs):
    if instance.type == Images.ImageType.input:
        work_image.delay(instance.id)

@receiver(pre_save, sender=ProcessingRequest)
def webhook_request(sender,instance,**kwargs):
    request = ProcessingRequest.objects.filter(id=instance.id).first()
    if request is None:
        return None
    if request.status==ProcessingRequest.ProcessingStatus.IN_PROGESS:
        if (instance.status == ProcessingRequest.ProcessingStatus.SUCCESS or 
            instance.status == ProcessingRequest.ProcessingStatus.FAILED):
            instance.completed_at = timezone.now()
            webhook.delay(request_id=request.id)
        