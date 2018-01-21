# -*- coding: UTF-8 -*-

from .models import *
from rest_framework import serializers

class SutraEntiySerializer(serializers.ModelSerializer):
    class Meta:
        model = SutraEntityModel
        fields = '__all__'
