from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User

def cadastro(request):
    template_name = 'cadastro.html'
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get('confirmar_senha')

        context = {
            'username': username,
            'email': email,
            'senha': senha,
            'confirmar_senha': confirmar_senha,
        }
        
        if len(username.strip()) == 0 or len(email.strip()) == 0 \
                or len(senha.strip()) == 0 or len(confirmar_senha.strip()) == 0:
            messages.add_message(request, messages.WARNING, 'Preencha todos os campos !')
            return render(request, template_name, context)
        
        if len(senha.strip()) < 6:
            messages.add_message(request, messages.WARNING, 'A senha deve conter 6 ou mais caracteres !')
            return render(request, template_name, context)

        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, messages.ERROR, 'Já existe um usuário com este username.')
            return render(request, template_name, context)

        users_email = User.objects.filter(email=email)

        if users_email.exists():
            messages.add_message(request, messages.ERROR, 'Já existe um usuário com este e-mail.')
            return render(request, template_name, context)

        if senha != confirmar_senha:
            messages.add_message(request, messages.ERROR, 'Senhas diferentes !')
            return render(request, template_name, context)

        if len(senha) < 6:
            messages.add_message(request, messages.ERROR, 'A senha deve conter 6 ou mais caracteres !')
            return render(request, template_name, context)
        
        try:
            User.objects.create_user(
                username=username.lower(),
                email=email,
                password=senha
            )
            messages.add_message(request, messages.SUCCESS, 'Cadastro efetuado com sucesso, efetue login.')
            return render(request, 'login.html', {'username': username})
            
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro: {e} !')

        return render(request, template_name, context)

    return render(request, template_name)
