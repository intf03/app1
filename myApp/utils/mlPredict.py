import math
import re

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from myApp.models import Products


ALGORITHM_INFO = {
    'linear': {
        'name': '线性回归预测',
        'model': 'sklearn.linear_model.LinearRegression',
        'desc': '使用价格、商品类型、发货地区和包邮状态作为特征，训练线性回归模型估算销量。',
    },
    'knn': {
        'name': 'KNN近邻回归预测',
        'model': 'sklearn.neighbors.KNeighborsRegressor',
        'desc': '使用商品特征距离寻找相似样本，由近邻商品销量共同估算目标商品销量。',
    },
    'weighted': {
        'name': '相似度加权回归预测',
        'model': 'sklearn.linear_model.LinearRegression + sample_weight',
        'desc': '根据输入商品与历史样本的相似度生成样本权重，再训练加权线性回归模型。',
    },
    'tree': {
        'name': '决策树回归预测',
        'model': 'sklearn.tree.DecisionTreeRegressor',
        'desc': '使用决策树回归模型学习商品类型、价格、地区和包邮状态与销量之间的非线性关系。',
    },
    'forest': {
        'name': '随机森林回归预测',
        'model': 'sklearn.ensemble.RandomForestRegressor',
        'desc': '使用多棵决策树集成回归，降低单棵树模型波动，用于销量辅助预测。',
    },
}


def _parse_number(value):
    """把价格、销量等网页文本转换为数值，兼容 ￥、元、逗号和“万”。"""
    if value is None:
        return 0.0
    text = str(value).replace(',', '').replace('￥', '').replace('元', '').strip()
    if not text:
        return 0.0
    match = re.search(r'\d+(?:\.\d+)?', text)
    if not match:
        return 0.0
    number = float(match.group())
    if '万' in text:
        number *= 10000
    return number


def _normalize_delivery(value):
    if value in (1, '1', True, 'true', 'True', '包邮'):
        return '1'
    if value in (0, '0', False, 'false', 'False', '不包邮'):
        return '0'
    return ''


def _delivery_text(value):
    if value == '1':
        return '包邮'
    if value == '0':
        return '不包邮'
    return '不限'


def _round(value, digits=4):
    if value is None:
        return 0
    try:
        if math.isnan(float(value)) or math.isinf(float(value)):
            return 0
        return round(float(value), digits)
    except Exception:
        return 0


def _load_records():
    records = []
    for row in Products.objects.all():
        price = _parse_number(row.price)
        sales = _parse_number(row.buy_len)
        product_type = (row.type or '其他').strip() or '其他'
        address = (row.address or '暂无').strip() or '暂无'
        delivery = _normalize_delivery(row.isFreeDelivery)
        if price <= 0 or sales <= 0:
            continue
        records.append({
            'id': row.id,
            'title': row.title or '',
            'type': product_type,
            'price': price,
            'address': address,
            'delivery': delivery,
            'deliveryText': _delivery_text(delivery),
            'sales': sales,
        })
    return records


def _build_encoder():
    try:
        encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)

    return ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['price']),
            ('cat', encoder, ['type', 'address', 'delivery']),
        ],
        remainder='drop',
    )


def _build_model(algorithm, n_samples):
    if algorithm == 'knn':
        return KNeighborsRegressor(n_neighbors=max(1, min(5, n_samples)))
    if algorithm == 'tree':
        return DecisionTreeRegressor(max_depth=6, random_state=42)
    if algorithm == 'forest':
        return RandomForestRegressor(n_estimators=80, max_depth=8, random_state=42)
    return LinearRegression()


def _to_frame(records):
    return pd.DataFrame([{
        'price': item['price'],
        'type': item['type'],
        'address': item['address'],
        'delivery': item['delivery'],
    } for item in records])


def _input_to_frame(input_data):
    return pd.DataFrame([{
        'price': input_data['price'],
        'type': input_data['type'],
        'address': input_data['address'],
        'delivery': input_data['delivery'],
    }])


def _calc_distance(record, input_data, max_price):
    price_distance = abs(record['price'] - input_data['price']) / max(max_price, 1)
    type_distance = 0 if record['type'] == input_data['type'] else 0.9
    address_distance = 0 if record['address'] == input_data['address'] else 0.65
    delivery_distance = 0 if (not input_data['delivery'] or record['delivery'] == input_data['delivery']) else 0.45
    return price_distance + type_distance + address_distance + delivery_distance


def _similar_samples(records, input_data, limit=8):
    max_price = max([item['price'] for item in records] + [input_data['price'], 1])
    rows = []
    for item in records:
        distance = _calc_distance(item, input_data, max_price)
        rows.append({
            **item,
            'distance': _round(distance, 4),
            'weight': _round(math.exp(-distance * 1.5), 4),
        })
    rows.sort(key=lambda x: x['distance'])
    return rows[:limit]


def _sample_weights(records, input_data):
    max_price = max([item['price'] for item in records] + [input_data['price'], 1])
    return np.array([math.exp(-_calc_distance(item, input_data, max_price) * 1.5) + 0.05 for item in records])


def _safe_metrics(y_true, y_pred):
    if len(y_true) == 0:
        return {'mae': 0, 'rmse': 0, 'r2': 0}
    mae = mean_absolute_error(y_true, y_pred)
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred) if len(y_true) >= 2 else 0
    return {
        'mae': _round(mae, 2),
        'rmse': _round(rmse, 2),
        'r2': _round(r2, 4),
    }


def _chart_data(algorithm, records, input_data, prediction, similar):
    if algorithm == 'linear' or algorithm == 'weighted':
        points = sorted(records, key=lambda x: x['price'])[:12]
        result = [{'name': str(_round(item['price'], 1)), 'value': _round(item['sales'], 1)} for item in points]
        result.append({'name': '预测价' + str(_round(input_data['price'], 1)), 'value': _round(prediction, 1)})
        return result

    if algorithm == 'knn':
        return [{'name': '近邻' + str(index + 1), 'value': _round(item['sales'], 1)} for index, item in enumerate(similar)]

    if algorithm == 'tree' or algorithm == 'forest':
        groups = [
            ('类型+地区+包邮', lambda item: item['type'] == input_data['type'] and item['address'] == input_data['address'] and item['delivery'] == input_data['delivery']),
            ('类型+地区', lambda item: item['type'] == input_data['type'] and item['address'] == input_data['address']),
            ('商品类型', lambda item: item['type'] == input_data['type']),
            ('发货地区', lambda item: item['address'] == input_data['address']),
            ('全部样本', lambda item: True),
        ]
        result = []
        for name, fn in groups:
            matched = [item for item in records if fn(item)]
            avg = sum(item['sales'] for item in matched) / len(matched) if matched else 0
            result.append({'name': name, 'value': _round(avg, 1), 'count': len(matched)})
        return result

    return []


def run_ml_prediction(params):
    algorithm = (params.get('algorithm') or 'linear').strip()
    if algorithm not in ALGORITHM_INFO:
        algorithm = 'linear'

    records = _load_records()
    if len(records) < 3:
        return {
            'code': 1,
            'msg': '可用于机器学习训练的商品样本不足，至少需要 3 条包含有效价格和销量的数据',
            'data': {},
        }

    type_list = sorted(list({item['type'] for item in records if item['type']}))
    address_list = sorted(list({item['address'] for item in records if item['address']}))

    input_data = {
        'type': (params.get('type') or (type_list[0] if type_list else '其他')).strip(),
        'price': _parse_number(params.get('price') or 0),
        'address': (params.get('address') or (address_list[0] if address_list else '暂无')).strip(),
        'delivery': _normalize_delivery(params.get('delivery')),
    }
    if input_data['price'] <= 0:
        input_data['price'] = float(np.median([item['price'] for item in records]))

    X = _to_frame(records)
    y = np.array([item['sales'] for item in records])
    weights = _sample_weights(records, input_data)
    indices = np.arange(len(records))

    if len(records) >= 10:
        train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)
    else:
        train_idx, test_idx = indices, indices

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]
    w_train = weights[train_idx]

    pipeline = Pipeline(steps=[
        ('preprocess', _build_encoder()),
        ('model', _build_model(algorithm, len(train_idx))),
    ])

    if algorithm == 'weighted':
        pipeline.fit(X_train, y_train, model__sample_weight=w_train)
    else:
        pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    raw_prediction = float(pipeline.predict(_input_to_frame(input_data))[0])
    max_sales = max([item['sales'] for item in records] + [1])
    prediction = min(max(raw_prediction, 0), max_sales * 1.25)

    metrics = _safe_metrics(y_test, y_pred)
    similar = _similar_samples(records, input_data)
    history_average = sum(item['sales'] for item in records) / len(records)

    return {
        'code': 0,
        'msg': 'success',
        'data': {
            'algorithm': algorithm,
            'algorithmName': ALGORITHM_INFO[algorithm]['name'],
            'modelName': ALGORITHM_INFO[algorithm]['model'],
            'modelDescription': ALGORITHM_INFO[algorithm]['desc'],
            'predictionValue': _round(prediction, 1),
            'rawPredictionValue': _round(raw_prediction, 1),
            'historyAverage': _round(history_average, 1),
            'sampleCount': len(records),
            'trainCount': len(train_idx),
            'testCount': len(test_idx),
            'metrics': metrics,
            'input': {
                **input_data,
                'deliveryText': _delivery_text(input_data['delivery']),
            },
            'typeList': type_list,
            'addressList': address_list,
            'similarSamples': similar,
            'chartData': _chart_data(algorithm, records, input_data, prediction, similar),
        },
    }
