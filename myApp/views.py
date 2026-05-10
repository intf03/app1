import json
import hashlib
import time

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Products, User
from .utils import getScreenData


def _safe_positive_int(value, default):
    try:
        value = int(value)
        return value if value > 0 else default
    except Exception:
        return default


def _parse_body(request):
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except Exception:
            return {}
    return request.POST.dict()


def _encode_password(value):
    text = str(value or '')
    return 'sha256$' + hashlib.sha256(text.encode('utf-8')).hexdigest()


def _check_password(user, value):
    if not user:
        return False
    saved = user.password or ''
    if saved.startswith('sha256$'):
        return saved == _encode_password(value)
    return saved == str(value or '')


def _user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'createTime': user.createTime.strftime('%Y-%m-%d %H:%M:%S') if user.createTime else '',
    }


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
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
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
        return JsonResponse({'code': 500, 'msg': str(e)}, status=500)


@csrf_exempt
def login(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    data = _parse_body(request)
    username = (data.get('username') or data.get('account') or '').strip()
    password = (data.get('password') or data.get('pwd') or '').strip()
    if not username or not password:
        return JsonResponse({'code': 1, 'msg': '请输入用户名和密码'})
    user = User.objects.filter(username=username).first()
    if not user or not _check_password(user, password):
        return JsonResponse({'code': 1, 'msg': '用户名或密码错误'})
    if not (user.password or '').startswith('sha256$'):
        user.password = _encode_password(password)
        user.save(update_fields=['password'])
    return JsonResponse({
        'code': 0,
        'msg': '登录成功',
        'data': {
            'token': 'user_%s_%s' % (user.id, int(time.time())),
            'user': _user_to_dict(user)
        }
    })


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    data = _parse_body(request)
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    confirm_password = (data.get('confirmPassword') or '').strip()
    if not username:
        return JsonResponse({'code': 1, 'msg': '请输入用户名'})
    if len(username) < 3:
        return JsonResponse({'code': 1, 'msg': '用户名至少 3 位'})
    if not password:
        return JsonResponse({'code': 1, 'msg': '请输入密码'})
    if len(password) < 3:
        return JsonResponse({'code': 1, 'msg': '密码至少 3 位'})
    if password != confirm_password:
        return JsonResponse({'code': 1, 'msg': '两次密码不一致'})
    if User.objects.filter(username=username).exists():
        return JsonResponse({'code': 1, 'msg': '用户名已存在'})
    user = User.objects.create(username=username, password=_encode_password(password))
    return JsonResponse({'code': 0, 'msg': '注册成功', 'data': {'user': _user_to_dict(user)}})


@csrf_exempt
def changePassword(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    data = _parse_body(request)
    user_id = data.get('userId') or data.get('user_id')
    username = (data.get('username') or '').strip()
    old_password = (data.get('oldPassword') or '').strip()
    new_password = (data.get('newPassword') or '').strip()
    confirm_password = (data.get('confirmPassword') or '').strip()
    user = User.objects.filter(id=user_id).first() if user_id else User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({'code': 1, 'msg': '用户不存在'})
    if not old_password or not _check_password(user, old_password):
        return JsonResponse({'code': 1, 'msg': '原密码错误'})
    if not new_password:
        return JsonResponse({'code': 1, 'msg': '请输入新密码'})
    if len(new_password) < 3:
        return JsonResponse({'code': 1, 'msg': '新密码至少 3 位'})
    if new_password != confirm_password:
        return JsonResponse({'code': 1, 'msg': '两次新密码不一致'})
    if _check_password(user, new_password):
        return JsonResponse({'code': 1, 'msg': '新密码不能与原密码相同'})
    user.password = _encode_password(new_password)
    user.save(update_fields=['password'])
    return JsonResponse({'code': 0, 'msg': '密码修改成功', 'data': {'user': _user_to_dict(user)}})


def productList(request):
    if request.method != 'GET':
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    try:
        page = _safe_positive_int(request.GET.get('page'), 1)
        page_size = _safe_positive_int(request.GET.get('pageSize'), 10)
        page_size = min(page_size, 100)
        keyword = (request.GET.get('keyword') or '').strip()
        product_type = (request.GET.get('type') or '').strip()
        address = (request.GET.get('address') or '').strip()
        queryset = Products.objects.all().order_by('-id')
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(name__icontains=keyword) | Q(type__icontains=keyword) | Q(address__icontains=keyword))
        if product_type:
            queryset = queryset.filter(type__icontains=product_type)
        if address:
            queryset = queryset.filter(address__icontains=address)
        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        records = [_product_to_dict(item) for item in queryset[start:end]]
        type_list = list(Products.objects.exclude(type='').values_list('type', flat=True).distinct().order_by('type'))
        address_list = list(Products.objects.exclude(address='').values_list('address', flat=True).distinct().order_by('address'))
        return JsonResponse({'code': 0, 'msg': 'success', 'data': records, 'total': total, 'page': page, 'pageSize': page_size, 'typeList': type_list, 'addressList': address_list})
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': str(e), 'data': [], 'total': 0}, status=500)
