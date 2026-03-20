# Script para reinstalar el módulo EOS desde cero
# Ejecutar este script desde la línea de comandos de Odoo

# 1. Desinstalar el módulo si está instalado
# 2. Limpiar caché
# 3. Reinstalar

# Comandos para ejecutar en la terminal de Odoo:
# python odoo-bin -d tu_base_de_datos -u mi90_eos --stop-after-init
# python odoo-bin -d tu_base_de_datos -i mi90_eos --stop-after-init

print("Script de reinstalación del módulo EOS")
print("=" * 50)
print("1. Detén el servidor Odoo")
print("2. Ejecuta: python odoo-bin -d tu_base_de_datos -u mi90_eos --stop-after-init")
print("3. Ejecuta: python odoo-bin -d tu_base_de_datos -i mi90_eos --stop-after-init")
print("4. Inicia el servidor Odoo normalmente")
print("=" * 50)
