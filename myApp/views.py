from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

from .utils import getScreenData
def screenData(request):
    if request.method == 'GET':
        cityList, volumnList = getScreenData.getSquareData()
        getScreenData.getPieData()
        pieList = getScreenData.getPieData()
        mapData = getScreenData.getMapData()
        return JsonResponse({
            'cityList':cityList,
            'volumnList':volumnList,
            'pieList':pieList,
            'mapData':mapData
        })