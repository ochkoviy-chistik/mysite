from accounts.models import User
from django.http import JsonResponse
from django.contrib.auth import logout as user_logout

from app.models import Doc

# Create your views here.


def index(request):
    response = {'answer': 'Hello!'}
    return JsonResponse(response)


def documents(request):
    response = {
        'status': 'response',
        'documents': []
    }

    for doc in Doc.objects.all():
        response['documents'].append(
            doc.to_json()
        )

    return JsonResponse(response)


def is_authorize(request):
    response = {
        'status': 'response',
        'is_authorize': request.user.is_authenticated
    }

    return JsonResponse(response)


def get_user_info(request):
    response = {
        'status': 'response'
    }

    try:
        response['user'] = request.user.to_json()
    except AttributeError:
        response['status'] = 'error'
        response['code'] = 'Пока не придумал.'
        response['error'] = 'User not authorized.'

    return JsonResponse(response)


def logout(request):
    response = {'status': 'response'}
    if request.user.is_authenticated:
        response['info'] = f'Пользователь {request.user} разлогинен.'
        user_logout(request)
    else:
        response['info'] = 'Ничего не произошло.'

    return JsonResponse(response)


def login(request):
    response = {}

    if not request.user.is_authenticated:
        data = request.POST
        print(data)

    return JsonResponse(response)

