from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from Rate import models
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
import requests
import json
from ratelimit.decorators import ratelimit
from ratelimit.core import get_usage, is_ratelimited
import datetime
from django.http import JsonResponse



class RegisterUser(APIView):
    permission_classes = ()
    def post(self,request, format=None):
        if self.request.method == 'POST':
            username = self.request.POST.get('username', 'Null')
            password = self.request.POST.get('password')
            duplicate_users = User.objects.filter(username=username)
            if duplicate_users.exists():
                print("Username exists bro")
                return HttpResponse("Username Exists Man")
            else:
                #Create a new user with provided credentials
                user_create = User.objects.create_user(username=username,
                                 password=password)
                #Create access token for the user
                token = Token.objects.create(user=user_create)
                print(username)
                print(token.key)
                return(HttpResponse("Registration Successful for user "+username))

class RandomGen(APIView):
    permission_classes = (IsAuthenticated,)

    def dorandomgen():
        #Call fastapi endpoint and return random number
        ep = 'https://cloudsekfastapi.herokuapp.com/91ba2c3f3dd5241218d2f24a3b1bfe4ce84923cb'
        res = requests.get(ep)
        print(res.json())
        return(res.json())


    def get(self,request, format=None):

        model = models.Usercache
        auth = request.META['HTTP_AUTHORIZATION'][6:]

        #For first use of service or when hour limit has expired, create new hour limit cache
        if(models.Usercache.objects.filter(userkey=auth).exists()==False):
            new_entry = models.Usercache()
            new_entry.userkey = auth
            new_entry.limit = 5
            new_entry.hour_limit = 100
            new_entry.save()
            cache.set(auth,100,3600)

        #Get usage stats of the minute cache
        min = get_usage(request, group='Rate.views.RandomGen', fn=None, key='header:http-authorization', rate='5/m', method='GET', increment=True)
        print("Minutly usage",min)

        if(min['should_limit']==False):
            catch = models.CacheTable.objects.filter(cache_key=auth).values()
            print(list(catch))
            if(list(catch)[0]['expires']>=datetime.datetime.now(datetime.timezone.utc)):
                #If cache has not expired
                userfield = models.Usercache.objects.get(userkey=auth)
                userlimit = userfield.hour_limit
                if(userlimit>0):
                    newuserlimit = userlimit-1
                    userfield.hour_limit = newuserlimit
                    userfield.save()
                    num = RandomGen.dorandomgen()
                    return HttpResponse(num['Random'])
                else:
                    return HttpResponse("Limit for the hour reached.Please try again later",status=403)

            else:
                #If cache has expired
                models.Usercache.objects.filter(userkey=auth).delete()
                num = RandomGen.dorandomgen()
                return HttpResponse(num['Random'])
        else:
            return HttpResponse("Sorry, You have exceeded your burst limit",status=403)



class LimitLeft(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request, format=None):

        model = models.Usercache
        auth = request.META['HTTP_AUTHORIZATION'][6:]
        return_list = {}

        if(models.Usercache.objects.filter(userkey=auth).exists()):
            lim = models.Usercache.objects.filter(userkey=auth)
            return_list['Remaining_Requests'] = lim.values('hour_limit')[0]['hour_limit']
            # Return the number of requests left for the hour
            return JsonResponse(return_list,safe=False)
        else:
            return HttpResponse('100 Requests left for this hour')
