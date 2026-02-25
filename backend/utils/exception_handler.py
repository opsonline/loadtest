from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        if response.status_code == 400:
            # 处理验证错误
            error_messages = []
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    error_messages.append(f"{field}: {', '.join(errors)}")
                else:
                    error_messages.append(f"{field}: {errors}")
            
            return Response({
                'code': 400,
                'message': error_messages[0] if error_messages else '参数错误',
                'data': response.data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif response.status_code == 401:
            return Response({
                'code': 401,
                'message': '未认证，请重新登录',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        elif response.status_code == 403:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        elif response.status_code == 404:
            return Response({
                'code': 404,
                'message': '资源不存在',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({
                'code': response.status_code,
                'message': str(response.data) if response.data else '服务器错误',
                'data': None
            }, status=response.status_code)
    
    return Response({
        'code': 500,
        'message': '服务器内部错误',
        'data': str(exc)
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
