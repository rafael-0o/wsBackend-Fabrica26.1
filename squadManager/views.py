from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect

from .models import SquadMember
from .rickmorty_client import RickMortyClient
from .serializers import RegisterUserSerializer
from .utils import enrich_squad_members
import requests

def home_page(request):
    return render(request, "squadManager/home.html", {"user": request.user})


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


def logout_page(request):
    logout(request)
    return redirect("home_page")


@login_required(login_url="login_page")
def search_characters_page(request):
    characters = []
    search_error = None
    search_name = request.GET.get("name", "").strip()
    search_page = request.GET.get("page", "").strip()
    
    if search_name:
        try:
            client = RickMortyClient()
            result = client.search_characters(
                name=search_name or None,
                page=int(search_page) if search_page and search_page.isdigit() else None
            )
            characters = result.get("results", [])
            if not characters:
                search_error = "No characters found."
        except requests.RequestException:
            search_error = "Error connecting to API. Please try again."
    
    return render(request, "squadManager/search.html", {
        "characters": characters,
        "search_name": search_name,
        "search_page": search_page,
        "search_error": search_error,
    })


@login_required(login_url="login_page")
def recruit_character(request):
    if request.method == "POST":
        character_id = request.POST.get("character_id", "").strip()
        role = request.POST.get("role", "").strip()
        tactical_note = request.POST.get("tactical_note", "").strip()
        
        if not character_id or not character_id.isdigit():
            return redirect("search_characters")
        
        try:
            SquadMember.objects.create(
                user=request.user,
                character_id=int(character_id),
                role=role or "RECON",
                tactical_note=tactical_note
            )
            return redirect("squad_page")
        except IntegrityError:
            return render(
                request,
                "squadManager/search.html",
                {"search_error": "Esse personagem já está no seu squad."},
            )
    return redirect("search_characters")


@login_required(login_url="login_page")
def squad_page(request):
    squad_members = SquadMember.objects.filter(user=request.user)
    enriched_members = enrich_squad_members(squad_members)
    
    return render(request, "squadManager/squad.html", {
        "enriched_members": enriched_members,
    })


@login_required(login_url="login_page")
def edit_squad_member(request, member_id):
    try:
        member = SquadMember.objects.get(id=member_id, user=request.user)
    except SquadMember.DoesNotExist:
        return redirect("squad_page")
    
    if request.method == "POST":
        role = request.POST.get("role", "").strip()
        tactical_note = request.POST.get("tactical_note", "").strip()
        
        if role:
            member.role = role
        member.tactical_note = tactical_note
        member.save()
        return redirect("squad_page")
    
    return render(request, "squadManager/edit_member.html", {"member": member})


@login_required(login_url="login_page")
def delete_squad_member(request, member_id):
    try:
        member = SquadMember.objects.get(id=member_id, user=request.user)
    except SquadMember.DoesNotExist:
        return redirect("squad_page")
    
    if request.method == "POST":
        member.delete()
        return redirect("squad_page")
    
    return render(request, "squadManager/delete_member.html", {"member": member})
    
   

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