# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.http import (HttpResponseRedirect, HttpResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as conf_settings
from django.core import serializers
from .models import UserToken
import datetime
import requests
import json
import jwt
import time

from .serializer import RegisterSerializer
from .decorators import token_authentication_required, refresh_token_authentication_required


SECRET_KEY = conf_settings.SECRET_KEY
JWT_ACCESS_TOKEN_LIFE_SPAN = conf_settings.JWT_ACCESS_TOKEN_LIFE_SPAN
JWT_REFRESH_TOKEN_LIFE_SPAN = conf_settings.JWT_REFRESH_TOKEN_LIFE_SPAN


def home(request):
    return HttpResponse("ok")


@api_view(['POST'])
@csrf_exempt
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            email=serializer.validated_data['email']
        )
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"message": "success", "data": serializer.data, "status": "201"}, status=status.HTTP_201_CREATED)
    return Response({"message": "error", "status": "400", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
def login(request):
    if not request.data:
        return Response({'message': "Please provide username/password"}, status=status.HTTP_400_BAD_REQUEST)
    username = request.data['username']
    password = request.data['password']

    try:
        user = User.objects.get(username=username)
        count_user_id = UserToken.objects.filter(user_id=user.id).count()
    except User.DoesNotExist:
        return Response({'message': "Invalid username/password"}, status=status.HTTP_400_BAD_REQUEST)

    passCheck = check_password(password, user.password)

    if user and passCheck:
        payload_access_token = getPayload(user.id, JWT_ACCESS_TOKEN_LIFE_SPAN)
        payload_refresh_token = getPayload(
            user.username, JWT_REFRESH_TOKEN_LIFE_SPAN)
        jwt_access_token = jwt.encode(
            payload_access_token, SECRET_KEY, algorithm='HS256')
        jwt_refresh_token = jwt.encode(
            payload_refresh_token, SECRET_KEY, algorithm='HS256')

        if int(count_user_id) > 0:
            UserToken.objects.filter(user_id=user.id).update(
                access_token=jwt_access_token, refresh_token=jwt_refresh_token)
        else:
            user_token_instance = UserToken(
                access_token=jwt_access_token, refresh_token=jwt_refresh_token, user_id=user.id)
            user_token_instance.save()

        token = {
            'access_token': jwt_access_token,
            'expires_in': JWT_ACCESS_TOKEN_LIFE_SPAN,
            'token_type': "Bearer",
            'refresh_token': jwt_refresh_token
        }

        return Response(
            token,
            status=status.HTTP_200_OK,
            content_type="application/json"
        )
    else:
        return Response(
            {'message': "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
            content_type="application/json"
        )


def getPayload(info, timeDelta):
    payload = {
        'info': info,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=timeDelta)
    }
    return payload


@api_view(['GET'])
@token_authentication_required
def get_user_info(request):
    user_id = request.session['user_id']
    users = User.objects.filter(id=user_id)
    user_list = []
    for user in users:
        user_dict = {}
        user_dict['username'] = user.username
        user_list.append(user_dict)
    return Response({
        "message": "success",
        "data": user_list[0],
        "status": "200"
    }, status=status.HTTP_200_OK, content_type="application/json")


@api_view(['GET'])
@refresh_token_authentication_required
def refresh(request):
    username = request.session['username']
    user_id = get_id_by_username(username)
    payload_access_token = getPayload(user_id, JWT_ACCESS_TOKEN_LIFE_SPAN)
    jwt_access_token = jwt.encode(
        payload_access_token, SECRET_KEY, algorithm='HS256')
    UserToken.objects.filter(user_id=user_id).update(
        access_token=jwt_access_token)
    token = {
        'access_token': jwt_access_token,
        'expires_in': JWT_ACCESS_TOKEN_LIFE_SPAN,
        'token_type': "Bearer",
    }
    return Response(
        token,
        status=status.HTTP_200_OK,
        content_type="application/json"
    )


def get_id_by_username(username):
    users = User.objects.filter(username=username)
    for user in users:
        user_id = user.id
    return user_id
