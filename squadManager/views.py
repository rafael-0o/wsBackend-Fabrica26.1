from django.db import IntegrityError
from django.shortcuts import render

from .serializers import RegisterUserSerializer


def home_page(request):
    return render(request, "squadManager/home.html")


def squad_page(request):
    return render(request, "squadManager/squad.html")


def register_page(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        serializer = RegisterUserSerializer(
            data={"username": username, "password": password}
        )
        if not serializer.is_valid():
            first_err = None
            for _field, msgs in serializer.errors.items():
                if msgs:
                    first_err = str(msgs[0])
                    break
            return render(
                request,
                "squadManager/register.html",
                {
                    "error": first_err or "Dados inválidos.",
                    "username": username,
                },
                status=400,
            )
        try:
            serializer.save()
        except IntegrityError:
            return render(
                request,
                "squadManager/register.html",
                {
                    "error": "Esse nome de usuário já está em uso.",
                    "username": username,
                },
                status=400,
            )
        return render(
            request,
            "squadManager/register.html",
            {"success": "Conta criada! Você já pode fazer login na home."},
        )
    return render(request, "squadManager/register.html")
