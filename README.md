# Rick & Morty Squad Manager

API em Django + DRF para montar um squad com personagens de Rick and Morty.

O projeto separa:
- dados externos (nome, imagem, especie, status): [Rick and Morty API](https://rickandmortyapi.com/)
- dados privados no banco (por usuario): `role` e `tactical_note`

---

## O que voce consegue fazer

- cadastrar usuario
- autenticar com JWT
- criar, listar, editar e remover membros do seu squad
- consultar squad enriquecido com dados completos dos personagens
- usar paginas web simples para testar o fluxo sem Postman

---

## Stack

- Python + Django `6.0.3`
- Django REST Framework `3.16.1`
- JWT com `djangorestframework-simplejwt`
- `requests` para consumir a API externa
- Banco:
  - SQLite (dev local simples)
  - PostgreSQL (via Docker)

---

## Modelo principal

`SquadMember` guarda:
- `user`
- `character_id`
- `role` (`LEAD | TANK | SUPP | RECON`)
- `tactical_note`
- `created_at`

Regra importante:
- combinacao `user + character_id` e unica (`UniqueConstraint`)
- um usuario nao pode recrutar o mesmo personagem duas vezes

---

## Estrutura de views

- `squadManager/views_api.py`: endpoints REST
- `squadManager/views_web.py`: paginas/template views

---

## Endpoints

Base URL local: `http://localhost:8000`

Para endpoints protegidos, envie:

`Authorization: Bearer <access_token>`

### Auth

- `POST /api/auth/register/` -> cria usuario
- `POST /api/auth/token/` -> retorna `access` + `refresh`
- `POST /api/auth/token/refresh/` -> renova `access`

Exemplo (`/api/auth/token/`):

```json
{
  "username": "seu_user",
  "password": "sua_senha"
}
```

### Squad (JWT)

- `GET /api/squad/`
- `POST /api/squad/`
- `GET /api/squad/<id>/`
- `PATCH /api/squad/<id>/`
- `DELETE /api/squad/<id>/`
- `GET /api/squad/enriched/`

Exemplo de criacao:

```json
{
  "character_id": 1,
  "role": "RECON",
  "tactical_note": "Alta mobilidade."
}
```

### Proxy da Rick and Morty API (publico)

- `GET /api/rickmorty/character/<id>/`
- `GET /api/rickmorty/characters/?name=<nome>&page=<n>`

### Registro legado no namespace rickmorty

- `POST /api/rickmorty/auth/register` (mesma funcionalidade de `/api/auth/register/`)

### Paginas web

- `GET /api/web/` -> home
- `GET /api/web/register/` -> registro
- `GET /api/web/squad/` -> squad do usuario logado

---

## Como rodar (Docker + Postgres)

Pre-requisito: Docker Desktop em execucao.

```bash
docker compose up --build
```

A API sobe em `http://localhost:8000` e executa `migrate` automaticamente.

Se aparecer erro do tipo `dockerDesktopLinuxEngine ... pipe ... nao encontrado`, o Docker Desktop nao esta ativo.

---

## Como rodar (local, SQLite)

1. Criar ambiente virtual

```bash
python -m venv venv
```

2. Ativar ambiente virtual

- Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Rodar migracoes

```bash
python manage.py migrate
```

5. (Opcional) criar superusuario

```bash
python manage.py createsuperuser
```

6. Subir servidor

```bash
python manage.py runserver
```

---

## Fluxo rapido de teste

1. criar usuario em `/api/auth/register/`
2. obter token em `/api/auth/token/`
3. usar token para `POST /api/squad/`
4. abrir `/api/squad/enriched/` para ver dados completos do personagem
5. testar UI em `/api/web/`

---

## Variaveis de ambiente

Principais:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Obs.: quando `POSTGRES_DB` existe no ambiente, o projeto usa PostgreSQL; caso contrario, usa SQLite.
