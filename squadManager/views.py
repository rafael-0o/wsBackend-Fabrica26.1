from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect

from .models import SquadMember
from .rickmorty_client import RickMortyClient
from .serializers import RegisterUserSerializer
from .utils import enrich_squad_members

def home_page(request):
    return render(request, "squadManager/index.html", {"user": request.user})

@login_required(login_url="login_page")
def squad_page(request):
    squad_members = SquadMember.objects.filter(user=request.user)
    enriched_members = enrich_squad_members(squad_members)
    
    return render(request, "squadManager/squad.html", {
        "enriched_members": enriched_members,
    })

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

def login_page(request):
    if request.user.is_authenticated:
        return redirect("home_page")
    
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            return render(
                request,
                "squadManager/login.html",
                {
                    "error": "Invalid username or password.",
                    "username": username,
                },
                status=401,
            )
    return render(request, "squadManager/login.html")
