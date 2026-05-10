from django.http import JsonResponse
from .utils import getScreenData


def screenData(request):
    if request.method != 'GET':
        return JsonResponse({
            'code': 405,
            'msg': 'method not allowed'
        }, status=405)

    try:
        cityList, volumnList = getScreenData.getSquareData()
        pieList = getScreenData.getPieData()
        mapData = getScreenData.getMapData()
        priceRangeList, priceRangeValueList = getScreenData.getPriceRangeData()
        typeSalesList = getScreenData.getTypeSalesData()

        return JsonResponse({
            'code': 0,
            'msg': 'success',
            'cityList': cityList,
            'volumnList': volumnList,
            'pieList': pieList,
            'mapData': mapData,
            'priceRangeList': priceRangeList,
            'priceRangeValueList': priceRangeValueList,
            'typeSalesList': typeSalesList,
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': str(e)
        }, status=500)
