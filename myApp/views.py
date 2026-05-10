from django.db.models import Q
from django.http import JsonResponse

from .models import Products
from .utils import getScreenData


def _safe_positive_int(value, default):
    try:
        value = int(value)
        return value if value > 0 else default
    except Exception:
        return default


def _product_to_dict(item):
    return {
        'id': item.id,
        'type': item.type or '',
        'title': item.title or '',
        'price': item.price or '',
        'buy_len': item.buy_len or '',
        'img_src': item.img_src or '',
        'name': item.name or '',
        'address': item.address or '',
        'isFreeDelivery': item.isFreeDelivery or '',
        'href': item.href or '',
        'nameHref': item.nameHref or '',
    }


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


def productList(request):
    """商品数据来源列表：从 products 数据表读取，支持关键词、类型、地区和分页。"""
    if request.method != 'GET':
        return JsonResponse({
            'code': 405,
            'msg': 'method not allowed'
        }, status=405)

    try:
        page = _safe_positive_int(request.GET.get('page'), 1)
        page_size = _safe_positive_int(request.GET.get('pageSize'), 10)
        page_size = min(page_size, 100)

        keyword = (request.GET.get('keyword') or '').strip()
        product_type = (request.GET.get('type') or '').strip()
        address = (request.GET.get('address') or '').strip()

        queryset = Products.objects.all().order_by('-id')

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(name__icontains=keyword) |
                Q(type__icontains=keyword) |
                Q(address__icontains=keyword)
            )

        if product_type:
            queryset = queryset.filter(type__icontains=product_type)

        if address:
            queryset = queryset.filter(address__icontains=address)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        records = [_product_to_dict(item) for item in queryset[start:end]]

        type_list = list(
            Products.objects.exclude(type='')
            .values_list('type', flat=True)
            .distinct()
            .order_by('type')
        )
        address_list = list(
            Products.objects.exclude(address='')
            .values_list('address', flat=True)
            .distinct()
            .order_by('address')
        )

        return JsonResponse({
            'code': 0,
            'msg': 'success',
            'data': records,
            'total': total,
            'page': page,
            'pageSize': page_size,
            'typeList': type_list,
            'addressList': address_list,
        })
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': str(e),
            'data': [],
            'total': 0,
        }, status=500)
