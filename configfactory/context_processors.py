from django.contrib.auth.context_processors import auth


def users(request):
    context = auth(request)
    user = context.pop('user', None)
    context['current_user'] = user
    return context
