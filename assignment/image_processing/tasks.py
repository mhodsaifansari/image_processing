import io
import json
import uuid
from celery import shared_task
import requests

from image_processing.models import ProcessingRequest,Images,SKUItem, Setting
# from image_processing.service import Service
from PIL import Image,UnidentifiedImageError

from django.core.files.uploadedfile import InMemoryUploadedFile

@shared_task()
def process_images(request_id):
    request = ProcessingRequest.objects.get(id=request_id)
    images = Images.objects.filter(sku__in=SKUItem.objects.filter(request=request),type=Images.ImageType.input)
    request.status = ProcessingRequest.ProcessingStatus.IN_PROGESS
    request.save()
    for image in images:
        r = requests.get(image.image_url, stream=True)
        r.raise_for_status()
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            img_io = io.BytesIO()
            img.save(img_io,format='jpeg',quality=50)
            compressed_image = Images(sku=image.sku, type=Images.ImageType.processed)
            file=InMemoryUploadedFile(img_io, field_name=None,name=f'{uuid.uuid4()}.jpeg', content_type='image/jpeg', size=img_io.tell, charset=None)
            compressed_image.image=file
            compressed_image.save()
    
    request.status = ProcessingRequest.ProcessingStatus.SUCCESS
    request.save()


@shared_task()
def work_image(image_id):
        
        image = Images.objects.filter(id=image_id).first()
        request = ProcessingRequest.objects.get(id=image.sku.request.id)
        if request.status == ProcessingRequest.ProcessingStatus.PENDING:
            request.status = ProcessingRequest.ProcessingStatus.IN_PROGESS
            request.save()
        if request.status == ProcessingRequest.ProcessingStatus.FAILED:
            print("failed")
            return 
        if image is None:
            return 
        # request = image.sku.request
        
        r = requests.get(image.image_url, stream=True)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            print(e)
            
            request.failure_reason = str(e)
            request.status = ProcessingRequest.ProcessingStatus.FAILED
            request.save()
            return 

        try:
            img = Image.open(io.BytesIO(r.content))
            img_io = io.BytesIO()
            img.save(img_io,format='jpeg',quality=50)
            compressed_image = Images(sku=image.sku, type=Images.ImageType.processed)
            file=InMemoryUploadedFile(img_io, field_name=None,name=f'{uuid.uuid4()}.jpeg', content_type='image/jpeg', size=img_io.tell, charset=None)
            compressed_image.image=file
            compressed_image.save()
            input_image = Images.objects.filter(sku__request=request,type=Images.ImageType.input).count()
            processe_image = Images.objects.filter(sku__request=request,type=Images.ImageType.processed).count()
            print(input_image)
            print(processe_image)
            print(request.image_count)
            if input_image == processe_image and request.image_count == processe_image:
                request.status = ProcessingRequest.ProcessingStatus.SUCCESS
                request.save()

        except UnidentifiedImageError as e:
            print("invalid image")
            request.failure_reason = f"Invalid Image URl: {image.image_url}"
            request.status = ProcessingRequest.ProcessingStatus.FAILED
            request.save()
            print(request.status)
            return 
        except Exception as e:
            print(e)
            request.failure_reason = str(e)
            request.status = ProcessingRequest.ProcessingStatus.FAILED
            request.save()
            print(request.status)
            return 
        
       

@shared_task
def webhook(request_id):
    setting = Setting.objects.first()
    if setting is None:
        setting = Setting(url="http://127.0.0.1:8000/webhookasdsad")
        setting.save()
    url = setting.url
    image_request = ProcessingRequest.objects.filter(id=request_id).first()
    if image_request is None:
        return None
    webhook_request = {'id':str(request_id),'status':image_request.status}
    res=requests.get(url+'asds')
    status_code = res.status_code
    try:
        response_body = res.json()
    except Exception as e:
        print(e)
        response_body=None
    print(status_code)
    print(response_body)
    image_request.webhook_request = json.dumps(webhook_request)
    image_request.webhook_status = status_code
    image_request.webhook_response = json.dumps(response_body)
    image_request.save()
    return None