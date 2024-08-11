# START.SE

> Projeto desenvolvido na [PSW 11](https://pythonando.com.br "Pythonando").

## Objetivo

    Conectar startups a investidores.

## Sumário

- <a href='#pré-requesitos'>Pré-requisitos</a>
- <a href='#funcionalidades'>Funcionalidades</a>
- <a href='#screenshots'>screenshots</a>
- <a href='#como-executar-o-projeto'>Como executar o projeto</a>

### Pré-requisitos

    Django, python-decouple e htmx.

### Funcionalidades

- Cadastro de usuários
- Login do usuário
- Cadastro empresas
- Lista empresas
- Ver empresa
- Sugestões de empresas para investidores
- Realizar proposta de investimento
- Assinar contrato
- Lista de propostas do investidor
- Dashboard

### Screenshots

|<img src="screenshots/cadastro_usuario.jpg" width="250">| &nbsp;&nbsp;<img src="screenshots/login_usuario.jpg" width="250">|
|<img src="screenshots/cadastro_empresa.jpg" width="250">| &nbsp;&nbsp;<img src="screenshots/lista_empresas.jpg" width="250">
|<img src="screenshots/ver_empresa.jpg" width="250">| &nbsp;&nbsp;<img src="screenshots/sugestoes.jpg" width="250">|
|<img src="screenshots/realizar_proposta.jpg" width="250">| &nbsp;&nbsp;<img src="screenshots/assinar_contrato.jpg" width="250">|
|<img src="screenshots/lista_propostas.jpg" width="250">| &nbsp;&nbsp;<img src="screenshots/dashboard.jpg" width="250">|

### Como executar o projeto

```bash
# Clone o projeto
git clone https://github.com/gm-costa/startse_psw11.git

# Renomeie o arquivo .env_sample
# No linux
mv .env_sample .env
# No windows
ren .env_sample .env

# Execute as migrações
python3 manage.py makemigrations && python3 manage.py migrate

# Execute o servidor
python3 manage.py runserver

# Teste o projeto, em um browser digite
http://127.0.0.1:8000

```

---
