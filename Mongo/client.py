#!/usr/bin/env python3
import os
import requests
import json

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("=" * 60)

def register_user():
    print("\n--- REGISTRO DE USUARIO ---")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    payload = {"username": username, "email": email, "password": password}
    resp = requests.post(f"{API_URL}/users", json=payload)
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def update_profile():
    print("\n--- ACTUALIZAR PERFIL ---")
    email = input("tu correo: ").strip()
    payload = {}

    bio = input("nueva bio (enter para saltar): ").strip()
    if bio: payload["bio"] = bio

    pic = input("nueva foto de perfil URL (enter para saltar): ").strip()
    if pic: payload["profile_pic"] = pic

    username = input("nuevo username (enter para saltar): ").strip()
    if username: payload["username"] = username

    if not payload:
        print("no cambiaste nada")
        return

    resp = requests.put(f"{API_URL}/users/{email}", json=payload)
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def create_post():
    print("\n--- CREAR POST ---")
    email = input("tu correo: ").strip()
    content = input("que quieres publicar: ").strip()
    image = input("URL de imagen (enter para saltar): ").strip()
    hashtags_str = input("hashtags separados por coma (enter para saltar): ").strip()

    hashtags = [h.strip() for h in hashtags_str.split(",")] if hashtags_str else []

    payload = {
        "user_id": email,
        "content": content,
        "image": image,
        "hashtags": hashtags
    }
    resp = requests.post(f"{API_URL}/posts", json=payload)
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def get_user_posts():
    print("\n--- POSTS DE UN USUARIO ---")
    email = input("correo del usuario: ").strip()
    resp = requests.get(f"{API_URL}/posts", params={"user_id": email})
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def search_content():
    print("\n--- BUSCAR EN POSTS ---")
    keyword = input("que palabra quieres buscar: ").strip()
    resp = requests.get(f"{API_URL}/posts", params={"search": keyword})
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def get_by_hashtag():
    print("\n--- BUSCAR POR HASHTAG ---")
    hashtag = input("hashtag a buscar (ej. tech): ").strip()
    resp = requests.get(f"{API_URL}/posts", params={"hashtag": hashtag})
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def get_trends():
    print("\n--- HASHTAGS MAS USADOS ---")
    resp = requests.get(f"{API_URL}/trends")
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def update_preferences():
    print("\n--- ACTUALIZAR PREFERENCIAS ---")
    email = input("tu correo: ").strip()
    
    print("\nPreferencias actuales:")
    resp = requests.get(f"{API_URL}/users/{email}/preferences")
    if resp.status_code == 200:
        print_json(resp.json())
    
    print("\nNuevas preferencias (enter para mantener):")
    theme = input("tema (light/dark): ").strip()
    notifications = input("notificaciones (true/false): ").strip()
    language = input("idioma (es/en): ").strip()
    
    payload = {}
    if theme: payload["theme"] = theme
    if notifications: payload["notifications"] = notifications.lower() == "true"
    if language: payload["language"] = language
    
    if not payload:
        print("no cambiaste nada")
        return
    
    resp = requests.put(f"{API_URL}/users/{email}/preferences", json=payload)
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def update_privacy():
    print("\n--- CONFIGURAR PRIVACIDAD ---")
    email = input("tu correo: ").strip()
    
    print("\nConfiguracion actual:")
    resp = requests.get(f"{API_URL}/users/{email}/privacy")
    if resp.status_code == 200:
        print_json(resp.json())
    
    print("\nNueva configuracion (enter para mantener):")
    visibility = input("visibilidad del perfil (public/private): ").strip()
    show_email = input("mostrar correo (true/false): ").strip()
    allow_messages = input("permitir mensajes (true/false): ").strip()
    
    payload = {}
    if visibility: payload["profile_visibility"] = visibility
    if show_email: payload["show_email"] = show_email.lower() == "true"
    if allow_messages: payload["allow_messages"] = allow_messages.lower() == "true"
    
    if not payload:
        print("no cambiaste nada")
        return
    
    resp = requests.put(f"{API_URL}/users/{email}/privacy", json=payload)
    print(f"Status: {resp.status_code}")
    print_json(resp.json())

def main():
    while True:
        print("\n" + "*" * 40)
        print("    MENU DE PRUEBAS")
        print("*" * 40)
        print("1. Registrar usuario")
        print("2. Actualizar perfil")
        print("3. Crear post")
        print("4. Ver posts de un usuario")
        print("5. Buscar en contenido")
        print("6. Buscar por hashtag")
        print("7. Ver tendencias")
        print("8. Actualizar preferencias")
        print("9. Configurar privacidad")
        print("10. Salir")

        opcion = input("\nelige una opcion: ").strip()

        if opcion == "1": register_user()
        elif opcion == "2": update_profile()
        elif opcion == "3": create_post()
        elif opcion == "4": get_user_posts()
        elif opcion == "5": search_content()
        elif opcion == "6": get_by_hashtag()
        elif opcion == "7": get_trends()
        elif opcion == "8": update_preferences()
        elif opcion == "9": update_privacy()
        elif opcion == "10":
            print("hasta luego!")
            break
        else:
            print("opcion no valida, intenta de nuevo")

if __name__ == "__main__":
    main()
