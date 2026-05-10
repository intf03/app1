import re
from .getBaseData1 import *


def safe_int(value):
    """把销量字段转换成整数，兼容空值、字符串、带逗号或异常内容。"""
    if value is None:
        return 0

    text = str(value).replace(',', '').strip()
    if not text:
        return 0

    match = re.search(r'\d+(?:\.\d+)?', text)
    if not match:
        return 0

    try:
        return int(float(match.group()))
    except Exception:
        return 0


def safe_float(value):
    """把价格字段转换成浮点数，兼容空值、字符串和带符号内容。"""
    if value is None:
        return 0

    text = str(value).replace(',', '').strip()
    if not text:
        return 0

    match = re.search(r'\d+(?:\.\d+)?', text)
    if not match:
        return 0

    try:
        return float(match.group())
    except Exception:
        return 0


def getSquareData():
    """各地区销售数据：按地区汇总销量。"""
    products = list(getAllProducts())
    productsVolumn = {}

    for item in products:
        address = item.address or '暂无'
        buy_len = safe_int(item.buy_len)
        productsVolumn[address] = productsVolumn.get(address, 0) + buy_len

    productsVolumn = sorted(productsVolumn.items(), key=lambda x: x[1], reverse=True)

    cityList = []
    volumnList = []
    for item in productsVolumn:
        cityList.append(item[0])
        volumnList.append(item[1])

    return cityList[:7], volumnList[:7]


def getPieData():
    """各类型产品数量占比。"""
    products = list(getAllProducts())
    productsNumber = {}

    for item in products:
        product_type = item.type or '其他'
        productsNumber[product_type] = productsNumber.get(product_type, 0) + 1

    pieList = []
    for key, value in productsNumber.items():
        pieList.append({
            'name': key,
            'value': value,
        })

    return pieList


def getMapData():
    """地图散点数据：按地区统计商品数量。"""
    products = list(getAllProducts())
    cityVolume = {}

    for item in products:
        address = item.address or '暂无'
        cityVolume[address] = cityVolume.get(address, 0) + 1

    mapData = []
    for key, value in cityVolume.items():
        mapData.append({
            'name': key,
            'value': value
        })

    return mapData


def getPriceRangeData():
    """商品价格占比模块：按价格区间统计商品数量。"""
    products = list(getAllProducts())

    priceRangeList = ['0-100', '100-200', '200-500', '500-1000', '千元以上']
    priceRangeValueList = [0, 0, 0, 0, 0]

    for item in products:
        price = safe_float(item.price)

        if price < 100:
            priceRangeValueList[0] += 1
        elif price < 200:
            priceRangeValueList[1] += 1
        elif price < 500:
            priceRangeValueList[2] += 1
        elif price < 1000:
            priceRangeValueList[3] += 1
        else:
            priceRangeValueList[4] += 1

    return priceRangeList, priceRangeValueList


def getTypeSalesData():
    """各类型销售量占比模块：按商品类型汇总销量。"""
    products = list(getAllProducts())
    typeSales = {}

    for item in products:
        product_type = item.type or '其他'
        buy_len = safe_int(item.buy_len)
        typeSales[product_type] = typeSales.get(product_type, 0) + buy_len

    result = []
    for key, value in typeSales.items():
        result.append({
            'name': key,
            'value': value
        })

    result = sorted(result, key=lambda x: x['value'], reverse=True)
    return result
