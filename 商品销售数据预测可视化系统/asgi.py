"""
ASGI config for 商品销售数据预测可视化系统 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '商品销售数据预测可视化系统.settings')

application = get_asgi_application()
