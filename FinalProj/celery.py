from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o módulo de configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Usa uma string aqui para não ter que serializar a configuração da configuração
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega os módulos de tarefa de todos os aplicativos Django
app.autodiscover_tasks()