from .getBaseData1 import *
def getSquareData():
    products = list(getAllProducts())
    productsVolumn = {}
    for i in products:
        if productsVolumn.get(i.address, -1):
            productsVolumn[i.address] = int(i.buy_len)
        else:
            productsVolumn[i.address] += int(i.buy_len)
    productsVolumn = sorted(productsVolumn.items(),key=lambda x:x[1],reverse=True)
    cityList = []
    volumnList = []
    for i in productsVolumn:
        cityList.append(i[0])
        volumnList.append(i[1])
    return cityList[:7],volumnList[:7]

def getPieData():
    products = list(getAllProducts())
    print(f"捕获到{len(products)}条数据")
    productsNumber = {}
    for i in products:
        if productsNumber.get(i.type, -1) == -1:
            productsNumber[i.type] = 1
        else:
            productsNumber[i.type] +=1
    pieList = []
    for k, v in productsNumber.items():
        pieList.append({
            'name': k,
            'value': v,
        })
    return pieList

def getMapData():
    products = list(getAllProducts())
    cityVolume = {}
    for i in products:
        if cityVolume.get(i.address, -1) == -1:
            cityVolume[i.address] = 1
        else:
            cityVolume[i.address] +=1
    mapData = []
    for k,v in cityVolume.items():
        mapData.append({
            'name':k,
            'value':v
        })
    return mapData