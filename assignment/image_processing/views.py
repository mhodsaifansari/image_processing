import csv
from django.http import HttpResponse
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser

from image_processing.models import Setting
from image_processing.service import Service
from image_processing.serializers import SettingSerializer, UploadSerializer
from rest_framework import status


# health
class Health(APIView):
    def get(self,request):
        return Response({"status":"system is active yayyy!!!"})


# get request
class UploadRequest(APIView):
    # parser_classes = [FileUploadParser]
    serialzier_class = [UploadSerializer]
    def post(self,request):
        serializer = UploadSerializer(data=request.data)
        return Service().generate_request(serializer=serializer)
        
        
class GetRequest(APIView):
    def get(self,request,id):
        return Service().get_status(request_body=request,request_id=id)

class GetCSV(APIView):
    def get(self,request,id):
        return Service().get_csv(request_body=request,request_id=id)

class SetWebhook(APIView):
    def get(self,request):
        setting = Setting.objects.first()
        return Response(SettingSerializer(setting).data, status=status.HTTP_200_OK)
    def post(self,request):
        setting = Setting.objects.first()
        print(request.data)
        if 'url' not in request.data:
            return Response({'status':'error','message':'url not in json body'})
        if setting is None:
            setting_obj = Setting(url=request.data['url'])
            setting_obj.save()
            return Response(SettingSerializer(setting_obj).data, status=status.HTTP_200_OK)
        else:
            setting.url = request.data['url']
            setting.save()
            return Response(SettingSerializer(setting).data, status=status.HTTP_200_OK)
    def delete(self,request):
        setting = Setting.objects.first()
        if setting:
            setting.delete()
        
        return Response({'status':'success','message':'setting deleted'})

# check status
class Webhook(APIView):
    def post(self,request):
        return Response({"status":"cool"})