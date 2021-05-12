from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from JianHong.models import UserInformation
from JianHong.viewsTool import getCache, NOT_LOGIN

REQUIRE_LOGIN = [
    '/jianhong/getMusicList/',
    '/jianhong/setMusicCollection/',
    '/jianhong/getUserInformation/',
]


class LoginMiddle(MiddlewareMixin):

    def process_request(self, request):

        print(request.path)

        if request.path == '/jianhong/getMusic/':
            token = request.GET.get("token")
            if token:
                user_id = getCache(token)
                if user_id:
                    try:
                        user = UserInformation.objects.get(pk=user_id)
                        request.user = user
                    except Exception:
                        return JsonResponse(status=status.HTTP_403_FORBIDDEN)
                else:
                    return JsonResponse(status=status.HTTP_403_FORBIDDEN)
            else:
                return JsonResponse(status=status.HTTP_403_FORBIDDEN)

        elif request.path in REQUIRE_LOGIN:
            token = request.GET.get("token")
            data = {
                "status": NOT_LOGIN,
                "msg": "not login",
            }
            if token:
                user_id = getCache(token)

                if user_id:
                    try:
                        user = UserInformation.objects.get(pk=user_id)
                        request.user = user
                    except Exception:
                        return JsonResponse(data=data)
                else:
                    return JsonResponse(data=data)
            else:
                data["status"] = 401
                data["msg"] = "not token"
                return JsonResponse(data=data)
