from django.shortcuts import redirect
from django.contrib import messages

def aprovado_required(view_func):
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'perfil') and request.user.perfil.aprovado:
            return view_func(request, *args, **kwargs)
        messages.warning(request, "Seu acesso ainda não foi aprovado.")
        return redirect('login')
    return wrapper
