#!/usr/bin/env python3
"""
Script de diagnóstico para el módulo mi90_eos
Ejecutar desde la raíz del proyecto Odoo
"""

import os
import sys

def check_module_structure():
    """Verificar la estructura del módulo"""
    print("🔍 Verificando estructura del módulo...")
    
    module_path = "mi_odoo_addons/mi90_eos"
    
    required_files = [
        "__manifest__.py",
        "__init__.py", 
        "models/__init__.py",
        "models/eos_dashboard.py",
        "security/ir.model.access.csv",
        "views/eos_menu.xml",
        "static/src/xml/dashboard.xml",
        "static/src/js/dashboard_action.js",
        "static/src/css/dashboard.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(module_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Todos los archivos requeridos están presentes")
        return True

def check_manifest():
    """Verificar el contenido del manifest"""
    print("\n🔍 Verificando __manifest__.py...")
    
    manifest_path = "mi_odoo_addons/mi90_eos/__manifest__.py"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que contiene las dependencias necesarias
        if '"web"' not in content:
            print("❌ Falta dependencia 'web' en el manifest")
            return False
            
        # Verificar que contiene los assets
        if 'web.assets_backend' not in content:
            print("❌ Falta configuración de assets en el manifest")
            return False
            
        print("✅ Manifest parece estar correcto")
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo manifest: {e}")
        return False

def generate_update_commands():
    """Generar comandos de actualización"""
    print("\n📋 Comandos para actualizar el módulo:")
    print("=" * 60)
    
    print("1. Detener el servidor Odoo")
    print("2. Ejecutar uno de estos comandos:")
    print()
    print("   # Opción A: Actualizar módulo")
    print("   python odoo-bin -d tu_base_de_datos -u mi90_eos --stop-after-init")
    print()
    print("   # Opción B: Reinstalar completamente")
    print("   python odoo-bin -d tu_base_de_datos -i mi90_eos --stop-after-init")
    print()
    print("   # Opción C: Limpiar caché y reinstalar")
    print("   python odoo-bin -d tu_base_de_datos -u base --stop-after-init")
    print("   python odoo-bin -d tu_base_de_datos -i mi90_eos --stop-after-init")
    print()
    print("3. Iniciar el servidor Odoo normalmente")
    print("4. Verificar que aparece el banner: 'Plantilla cargada: v2025-10-18-01'")
    print("=" * 60)

def main():
    print("🚀 Diagnóstico del módulo mi90_eos")
    print("=" * 50)
    
    # Verificar estructura
    structure_ok = check_module_structure()
    
    # Verificar manifest
    manifest_ok = check_manifest()
    
    if structure_ok and manifest_ok:
        print("\n✅ El módulo parece estar bien configurado")
        print("💡 Si no se ve el banner de verificación, prueba los comandos de actualización")
    else:
        print("\n❌ Se encontraron problemas en la configuración")
    
    # Generar comandos
    generate_update_commands()
    
    print("\n🔧 Si el problema persiste:")
    print("   1. Verifica que el módulo esté en la lista de módulos instalados")
    print("   2. Revisa los logs de Odoo para errores específicos")
    print("   3. Asegúrate de que la base de datos esté correcta")

if __name__ == "__main__":
    main()


