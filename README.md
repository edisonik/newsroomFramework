# newsroomFramework

## Como setar o ambiente

### Dê um clone do projeto e instale as dependências
* > git clone https://github.com/edisonik/newsroomFramework.git
* > cd newsroomFramework
* > sudo apt-get update
* > xargs -a dependencies.txt sudo apt-get install

### Instale o pip
  > sudo apt-get install python3-pip

### Depois instale o virtualenv usando pip3
  > sudo pip3 install virtualenv

### Configure o ambiente virtual
  > virtualenv –p /usr/bin/python3 virtualenv

### Ative o ambiente virtual
  > source virtualenv/bin/activate
  
### Instale os requerimentos utilizando o pip
  > pip install -r python_requirements.txt

### Configure o banco de dados
  * > mysql -u root -p
  * > CREATE USER ’seu_usuario’@’localhost’ IDENTIFIED BY ’sua_senha’;
  * > GRANT ALL PRIVILEGES ON *.* TO ’seu_usuario’@’localhost’ WITH GRANT OPTION;
  * > CREATE DATABASE cms CHARSET utf8;
  * > Em settings.py modifique as entradas USERNAME e PASSWORD do dicionário DATABASES para o usuário e senha escolhidos ,respectivamente.

### Faça as migrações pendentes
  > python manage.py migrate


## Como executar o ambiente

### Execute o servidor
  > python manage.py runserver
### Acesse o sistema pela seguinte url
  > http://127.0.0.1:8000/menu/
  
### Para acessar o sistema administrador do Django:
  * > Crie um usuário com o comando: python manage.py createsuperuser
  * > python manage.py runserver
  * > Acesse http://127.0.0.1:8000/admin/

## Para mais informações acesse a Wiki
