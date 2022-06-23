from django.http import JsonResponse
from rest_framework.views import APIView

from django_pat.rest_framework.permissions import PatPermission


class SampleApiView(APIView):
    http_method_names = ["get"]
    permission_classes = [PatPermission("django_pat.view_personalaccesstoken")]

    def get(self, request, *args, **kwargs):
        return JsonResponse({"result": "Yay"})
