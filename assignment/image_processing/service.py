
from django.urls import reverse
import pandas as pd
from image_processing.models import Images, ProcessingRequest, SKUItem
from image_processing.serializers import ProcessingRequestCompleted, ProcessingRequestCompletedWithWebhook, ProcessingRequestFailed, ProcessingRequestFailedWebhook, UploadSerializer
from rest_framework.response import Response
from rest_framework import status
from pandera import Column, DataFrameSchema, Check, Index,errors
from django.core.validators import URLValidator
from django.http import HttpResponse
from image_processing.models import Images, ProcessingRequest, SKUItem


def valid_url(s):
    try:
        url_validator = URLValidator()
        for url in s.split(','):
            url_validator(url)
        return True
    except Exception as e:
        return False
class Service:
    def __init__(self):
        pass

    def csv_schema(self)->DataFrameSchema:
        schema = DataFrameSchema(
            {
                "S.No.": Column(str),
                "Product Name": Column(str, Check(lambda x: x.strip() != "", element_wise=True)),
                # you can provide a list of validators
                "Input Image Urls": Column(str, [
                    Check(check_fn=valid_url,element_wise=True)
                ]),
            },
            index=Index(int),
            strict=True,
            coerce=True,
        )
        return schema
    def generate_request(self, serializer:UploadSerializer):
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        file = serializer.validated_data['file']
        try:
            reader = pd.read_csv(file)
        except Exception as e:
            return Response({"status":"error","message":"invalid csv"},status=status.HTTP_400_BAD_REQUEST)
        if reader.isnull().values.any():
            return Response({"status":"error","message":"csv contains null value"},status=status.HTTP_400_BAD_REQUEST)
        schema = self.csv_schema()
        try:
            schema.validate(reader)
        except errors.SchemaError as e:
            return Response({"status":"error","message":str(e)},status=status.HTTP_400_BAD_REQUEST)  
        images = list(reader['Input Image Urls'])
        image_count = sum([len(image_list.split(',')) for image_list in images])
        request = ProcessingRequest(status=ProcessingRequest.ProcessingStatus.PENDING,image_count=image_count)
        request.save()
        for _, row in reader.iterrows():
            sku = row['Product Name']
            images = row['Input Image Urls']
            sku = SKUItem(sku=sku,request=request)
            sku.save()
            for image in images.split(','):
                image_model = Images(sku=sku,type=Images.ImageType.input,image_url=image)
                image_model.save()

        return Response({"status":"success","request_id":request.id})
    
    def get_csv(self,request_body, request_id:str):
        request = ProcessingRequest.objects.get(id=request_id)
        if request.status!=ProcessingRequest.ProcessingStatus.SUCCESS:
            return Response({"msg":f"request in {request.status}"},status=status.HTTP_200_OK)
        sku_item = SKUItem.objects.filter(request=request)
        response_dict = {}
        data=[]
        i=1
        for sku in sku_item:
            input_images = Images.objects.filter(sku=sku,type=Images.ImageType.input)
            input_images  = ','.join([input.image_url for input in input_images])
            output_images = Images.objects.filter(sku=sku,type=Images.ImageType.processed)
            output_images = ','.join([request_body.build_absolute_uri(input.image.url) for input in output_images])
            response_dict[sku.sku]={'input_images':input_images,'output_images':output_images}
            data.append([f"{i}.",sku.sku,input_images,output_images])
            i+=1
        df = pd.DataFrame(data=data,columns=['S.No.','Product Name','Input Image Urls','Output Image Urls'])
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=result.csv'
        df.to_csv(path_or_buf=response,sep=',',index=False)
        return response
    
    def get_status(self,request_body, request_id:str):
        image_request = ProcessingRequest.objects.filter(id=request_id).first()
        if image_request is None:
            return Response({"status":"error","message":"Invalid Request ID"},status=status.HTTP_400_BAD_REQUEST)
        if image_request.status == ProcessingRequest.ProcessingStatus.SUCCESS:
            csv_url=request_body.build_absolute_uri(reverse('Get_CSV', args=(request_id, )))
            print(image_request.webhook_status)
            if image_request.webhook_status is None:
                return Response(ProcessingRequestCompleted(image_request,context={'csv_file':csv_url}).data,status=status.HTTP_200_OK)
            return Response(ProcessingRequestCompletedWithWebhook(image_request,context={'csv_file':csv_url}).data,status=status.HTTP_200_OK)
        else:
            if image_request.webhook_status is None: 
                return Response(ProcessingRequestFailed(image_request).data,status=status.HTTP_200_OK)
            else:
                return Response(ProcessingRequestFailedWebhook(image_request).data,status=status.HTTP_200_OK)

        
    
    
    
    
        