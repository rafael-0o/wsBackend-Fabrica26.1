# Rick & Morty Squad Manager API 🚀

Este projeto é uma API robusta desenvolvida em Django e Django REST Framework (DRF) para gerenciar esquadrões de personagens da série **Rick & Morty**. Ele integra dados da [Rick and Morty API](https://rickandmortyapi.com/) com informações personalizadas de cada usuário, permitindo a criação de equipes estratégicas.

---

## 🧐 O que o projeto faz e para que serve?

O **Rick & Morty Squad Manager** serve como uma ferramenta de gerenciamento onde usuários podem:
- **Criar uma conta e autenticar-se**: Sistema seguro com JWT.
- **Explorar personagens**: Consultar dados da API externa.
- **Recrutar para o Esquadrão**: Adicionar personagens ao seu time pessoal.
- **Atribuir Funções**: Definir se o personagem é um `LEAD`, `TANK`, `SUPP` ou `RECON`.
- **Adicionar Notas Táticas**: Escrever observações estratégicas para cada membro.
- **Visualizar Esquadrão Enriquecido**: Ver a lista de membros com todos os detalhes originais da série (imagem, status, espécie) + seus dados personalizados.

---

## 🛠️ Tecnologias Utilizadas

### Core & Frameworks
- **Python 3.12+**
- **Django 6.0.3**: Framework web principal.
- **Django REST Framework 3.16.1**: Para construção da API.
- **Simple JWT 5.5.1**: Autenticação baseada em tokens.

### Integrações & Documentação
- **Requests 2.32.3**: Consumo da API externa de Rick & Morty.
- **DRF Spectacular 0.28.0**: Geração automática de documentação OpenAPI/Swagger.

### Infraestrutura & Banco de Dados
- **PostgreSQL**: Banco de dados relacional para produção (via Docker).
- **SQLite**: Banco de dados local para desenvolvimento rápido.
- **Docker & Docker Compose**: Containerização completa da aplicação e banco de dados.

---

## ⚙️ Configuração Opcional (.env)

O projeto possui valores padrão para rodar localmente com SQLite, mas você pode customizar o comportamento usando um arquivo `.env` na raiz do projeto:

| Variável | Descrição | Padrão (Local) |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Chave secreta do Django | *django-insecure...* |
| `DJANGO_DEBUG` | Ativar/Desativar modo debug | `1` (Ligado) |
| `DJANGO_ALLOWED_HOSTS`| Hosts permitidos | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Nome do banco (apenas Docker) | `rickmorty` |
| `POSTGRES_USER` | Usuário do banco (apenas Docker) | `postgres` |
| `POSTGRES_PASSWORD` | Senha do banco (apenas Docker) | `postgres` |

---

## 🚀 Como Executar o Projeto

### 🐳 Via Docker (Recomendado)

1. **Suba os containers**:
   ```bash
   docker-compose up --build
   ```

2. **Execute as migrações e crie um administrador**:
   ```bash
   docker-compose exec api python manage.py migrate
   docker-compose exec api python manage.py createsuperuser
   ```

### 💻 Manualmente (Local)

1. **Crie um ambiente virtual e instale as dependências**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Prepare o banco e crie um administrador**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Inicie o servidor**:
   ```bash
   python manage.py runserver
   ```

---

## � Relacionamento de Dados

O projeto utiliza uma modelagem simplificada e eficiente:

- **Usuário (User) ↔️ Esquadrão (SquadMember)**: Relacionamento de **1:N** (Um para Muitos). Cada usuário autenticado possui seu próprio esquadrão, mas um membro do esquadrão pertence a apenas um usuário.
- **Membro do Esquadrão (SquadMember)**: Atua como uma tabela de junção entre o usuário do sistema e o `character_id` (ID externo da Rick & Morty API).
- **Integridade**: Existe uma restrição de unicidade (`UniqueConstraint`) que garante que um usuário não possa ter o mesmo personagem repetido em seu time.

---

## � Regras de Negócio e Detalhes Técnicos

- **Padrão de Desenvolvimento**: O código-fonte, variáveis, nomes de classes e comentários foram desenvolvidos inteiramente em **inglês**, seguindo o padrão pessoal de desenvolvimento para projetos técnicos.
- **Unicidade de Personagem**: Um usuário não pode recrutar o mesmo personagem (`character_id`) mais de uma vez para o seu esquadrão.
- **Dados Híbridos**: Informações como nome, espécie e imagem são buscadas em tempo real da [Rick and Morty API](https://rickandmortyapi.com/), enquanto `role` e `tactical_note` são armazenados localmente.
- **Painel Administrativo**: Disponível em `http://localhost:8000/admin/` para gerenciar usuários e membros do esquadrão diretamente.

---

## 🔌 Endpoints da API

### 🔐 Autenticação

#### **Registrar Usuário**
`POST /api/auth/register/`
- **Request JSON**:
```json
{
  "username": "morty_fan",
  "password": "secret_password"
}
```
- **Response (201 Created)**:
```json
{
  "id": 1,
  "username": "morty_fan",
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

#### **Login**
`POST /api/auth/login/`
- **Request JSON**:
```json
{
  "username": "morty_fan",
  "password": "secret_password"
}
```
- **Response (200 OK)**:
```json
{
  "id": 1,
  "username": "morty_fan",
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### 🛡️ Gerenciamento de Esquadrão (Requer JWT)
*Header: `Authorization: Bearer <seu_token_aqui>`*

#### **Listar Esquadrão**
`GET /api/squad/`
- Retorna os IDs dos personagens e dados locais do seu esquadrão.

#### **Recrutar Personagem**
`POST /api/squad/`
- **Request JSON**:
```json
{
  "character_id": 1,
  "role": "LEAD",
  "tactical_note": "O Rick original da C-137."
}
```
- **Roles Disponíveis**: `LEAD`, `TANK`, `SUPP`, `RECON`.

#### **Visualizar Detalhes**
`GET /api/squad/<id>/`

#### **Atualizar Membro**
`PATCH /api/squad/<id>/`
- **Exemplo**: Alterar apenas a nota tática.
```json
{
  "tactical_note": "Nova estratégia definida."
}
```

#### **Remover do Esquadrão**
`DELETE /api/squad/<id>/`

#### **Esquadrão Enriquecido**
`GET /api/squad/enriched/`
- Retorna os membros do seu esquadrão com todos os dados da API original de Rick & Morty inclusos.

---

## 📖 Documentação Automática

Acesse a documentação interativa da API para testar os endpoints diretamente do navegador:
- **Swagger UI**: `http://localhost:8000/api/docs/swagger/`
- **Redoc**: `http://localhost:8000/api/docs/redoc/`

---

## 🌐 Interface Web

O projeto também conta com uma interface web simples para testes rápidos:
- **Home**: `http://localhost:8000/api/web/`
- **Login**: `http://localhost:8000/api/web/login/`
- **Meu Esquadrão**: `http://localhost:8000/api/web/squad/`
- **Recrutar**: `http://localhost:8000/api/web/search/`
