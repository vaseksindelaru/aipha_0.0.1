#!/usr/bin/env python3
# aiphalab/aiphalab_cli.py
"""
AiphaLab - Interfaz CLI Profesional
Sistema de análisis de código con IA

Autor: AiphaLab Team
Versión: 1.0.0
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Colores ANSI para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Símbolos Unicode
class Symbols:
    CHECK = '✓'
    CROSS = '✗'
    ARROW = '→'
    BULLET = '•'
    STAR = '★'
    ROBOT = '🤖'
    FOLDER = '📁'
    FILE = '📄'
    SEARCH = '🔍'
    CHART = '📊'
    GEAR = '⚙️'
    ROCKET = '🚀'

def print_header():
    """Imprime el header de AiphaLab"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print(r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     █████╗ ██╗██████╗ ██╗  ██╗ █████╗ ██╗      █████╗   ║
    ║    ██╔══██╗██║██╔══██╗██║  ██║██╔══██╗██║     ██╔══██╗  ║
    ║    ███████║██║██████╔╝███████║███████║██║     ███████║  ║
    ║    ██╔══██║██║██╔═══╝ ██╔══██║██╔══██║██║     ██╔══██║  ║
    ║    ██║  ██║██║██║     ██║  ██║██║  ██║███████╗██║  ██║  ║
    ║    ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ║
    ║                                                           ║
    ║              Sistema de Análisis de Código con IA        ║
    ║                      Versión 1.0.0                        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_section(title: str):
    """Imprime un título de sección"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{Symbols.ARROW} {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.ENDC}\n")

def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}{Symbols.CHECK} {message}{Colors.ENDC}")

def print_error(message: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}{Symbols.CROSS} {message}{Colors.ENDC}")

def print_warning(message: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message: str):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}{Symbols.BULLET} {message}{Colors.ENDC}")

def print_menu(options: list):
    """Imprime un menú de opciones"""
    print(f"\n{Colors.BOLD}Selecciona una opción:{Colors.ENDC}\n")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.CYAN}{i}.{Colors.ENDC} {option}")
    print(f"\n  {Colors.CYAN}0.{Colors.ENDC} {Colors.RED}Salir{Colors.ENDC}")
    print()

class AiphaLabCLI:
    """
    Interfaz de línea de comandos profesional para AiphaLab
    """
    
    def __init__(self):
        self.config_file = Path.home() / ".aiphalab" / "config.json"
        self.config = self.load_config()
        self.shadow = None
        self.gemini = None
        
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Guardar configuración a archivo"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Verificar dependencias instaladas"""
        deps = {}
        
        try:
            import google.generativeai
            deps['gemini'] = True
        except ImportError:
            deps['gemini'] = False
        
        try:
            from shadow_hybrid import ShadowHybrid
            deps['shadow_hybrid'] = True
        except ImportError:
            deps['shadow_hybrid'] = False
        
        try:
            from shadow_query import ShadowQuery
            deps['shadow_query'] = True
        except ImportError:
            deps['shadow_query'] = False
        
        try:
            from memory_system import AiphaLabMemory
            deps['memory_system'] = True
        except ImportError:
            deps['memory_system'] = False
        
        return deps
    
    def check_api_key(self) -> bool:
        """Verificar API key de Gemini"""
        return os.getenv('GEMINI_API_KEY') is not None
    
    def find_aipha_directory(self) -> Optional[str]:
        """Auto-detectar directorio de Aipha_0.0.1"""
        locations = [
            Path("."),
            Path(".."),
            Path("../.."),
            Path.home() / "Aipha_0.0.1",
        ]
        
        for loc in locations:
            if (loc / "main.py").exists() and (loc / "potential_capture_engine.py").exists():
                return str(loc.resolve())
        
        return None
    
    def setup_wizard(self):
        """Asistente de configuración inicial"""
        print_header()
        print_section("Asistente de Configuración Inicial")
        
        # Verificar dependencias
        print_info("Verificando dependencias...")
        deps = self.check_dependencies()
        
        print()
        for dep, installed in deps.items():
            if installed:
                print_success(f"{dep}: Instalado")
            else:
                print_error(f"{dep}: No instalado")
        
        if not all(deps.values()):
            print_warning("\nAlgunas dependencias faltan. Instalar con:")
            print(f"  {Colors.CYAN}pip install google-generativeai{Colors.ENDC}")
            return False
        
        # Verificar API key
        print()
        print_info("Verificando API key de Gemini...")
        if self.check_api_key():
            api_key = os.getenv('GEMINI_API_KEY')
            masked_key = f"***{api_key[-4:]}"
            print_success(f"API Key configurada ({masked_key})")
        else:
            print_error("GEMINI_API_KEY no configurada")
            print_warning("Configurar con:")
            print(f"  {Colors.CYAN}export GEMINI_API_KEY='tu_api_key'{Colors.ENDC}")
            return False
        
        # Detectar directorio de Aipha
        print()
        print_info("Buscando directorio de Aipha_0.0.1...")
        aipha_dir = self.find_aipha_directory()
        
        if aipha_dir:
            print_success(f"Encontrado en: {aipha_dir}")
            self.config['aipha_path'] = aipha_dir
        else:
            print_warning("No se encontró automáticamente")
            path = input(f"\n{Colors.CYAN}Ingresa la ruta a Aipha_0.0.1: {Colors.ENDC}").strip()
            if Path(path).exists():
                self.config['aipha_path'] = path
                print_success("Ruta configurada")
            else:
                print_error("Ruta no válida")
                return False
        
        # Guardar configuración
        self.save_config()
        print()
        print_success("✨ Configuración completada exitosamente!")
        return True
    
    def initialize_shadow(self):
        """Inicializar Shadow"""
        if self.shadow is not None:
            return True
        
        try:
            from shadow_hybrid import ShadowHybrid
            print_info("Inicializando Shadow Híbrido...")
            aipha_path = self.config.get('aipha_path', '.')
            self.shadow = ShadowHybrid(aipha_path)
            print_success("Shadow inicializado")
            return True
        except Exception as e:
            print_error(f"Error inicializando Shadow: {e}")
            return False
    
    def initialize_gemini(self):
        """Inicializar Gemini"""
        if self.gemini is not None:
            return True
        
        try:
            from gemini_integration import GeminiShadow
            print_info("Inicializando Gemini...")
            aipha_path = self.config.get('aipha_path', '.')
            self.gemini = GeminiShadow(base_path=aipha_path)
            print_success("Gemini inicializado")
            return True
        except Exception as e:
            print_error(f"Error inicializando Gemini: {e}")
            return False
    
    def analyze_codebase(self):
        """Analizar codebase"""
        print_section("Análisis de Codebase")
        
        if not self.initialize_shadow():
            return
        
        print_info("Analizando código...")
        print_info("(Esto puede tomar unos momentos en la primera ejecución)")
        print()
        
        try:
            self.shadow.analyze_codebase(force=False)
            print()
            print_success("Análisis completado!")
            
            # Mostrar resumen
            overview = self.shadow.get_system_overview()
            print()
            print_info(f"Componentes analizados: {overview['total_components']}")
            print_info(f"Entradas en memoria: {overview['total_entries']}")
            
            if overview.get('last_update'):
                print_info(f"Última actualización: {overview['last_update']}")
        
        except Exception as e:
            print_error(f"Error durante análisis: {e}")
    
    def interactive_query(self):
        """Modo de consulta interactiva con Gemini"""
        print_section("Modo Interactivo con Gemini")
        
        if not self.initialize_gemini():
            return
        
        print_info("Modo interactivo iniciado")
        print_info("Escribe 'salir' para terminar")
        print()
        
        try:
            self.gemini.interactive_mode()
        except KeyboardInterrupt:
            print()
            print_info("Modo interactivo terminado")
    
    def show_overview(self):
        """Mostrar resumen del sistema"""
        print_section("Resumen del Sistema")
        
        if not self.initialize_shadow():
            return
        
        try:
            overview = self.shadow.get_system_overview()
            
            print(f"{Colors.BOLD}Sistema:{Colors.ENDC}")
            print_info(f"Componentes: {overview['total_components']}")
            print_info(f"Entradas: {overview['total_entries']}")
            
            if overview.get('last_update'):
                print_info(f"Última actualización: {overview['last_update']}")
            
            print()
            print(f"{Colors.BOLD}Componentes:{Colors.ENDC}")
            for component in overview.get('components', []):
                print(f"  {Colors.CYAN}{Symbols.FILE}{Colors.ENDC} {component}")
            
            print()
            print(f"{Colors.BOLD}Estado de MCPs:{Colors.ENDC}")
            mcp_status = overview.get('mcp_status', {})
            for mcp, status in mcp_status.items():
                if status:
                    print_success(f"{mcp}")
                else:
                    print_warning(f"{mcp}: No disponible")
        
        except Exception as e:
            print_error(f"Error obteniendo resumen: {e}")
    
    def search_code(self):
        """Buscar en el código"""
        print_section("Búsqueda en Código")
        
        if not self.initialize_shadow():
            return
        
        keyword = input(f"{Colors.CYAN}Término a buscar: {Colors.ENDC}").strip()
        if not keyword:
            print_warning("Búsqueda cancelada")
            return
        
        print()
        print_info(f"Buscando '{keyword}'...")
        
        try:
            results = self.shadow.search(keyword, search_type='hybrid')
            
            text_matches = results.get('text_matches', [])
            struct_matches = results.get('structural_matches', [])
            
            print()
            print_success(f"Encontrados {len(text_matches)} coincidencias de texto")
            print_success(f"Encontrados {len(struct_matches)} coincidencias estructurales")
            
            if struct_matches:
                print()
                print(f"{Colors.BOLD}Coincidencias estructurales:{Colors.ENDC}")
                for match in struct_matches[:10]:
                    print(f"  {Colors.CYAN}{match['type']}:{Colors.ENDC} {match['name']} "
                          f"en {match['component']}")
            
            if len(struct_matches) > 10:
                print_info(f"... y {len(struct_matches) - 10} más")
        
        except Exception as e:
            print_error(f"Error durante búsqueda: {e}")
    
    def show_stats(self):
        """Mostrar estadísticas"""
        print_section("Estadísticas")
        
        if not self.initialize_shadow():
            return
        
        try:
            from shadow_query import ShadowQuery
            shadow_query = ShadowQuery()
            
            complexity = shadow_query.get_complexity_analysis()
            
            print(f"{Colors.BOLD}Complejidad del Código:{Colors.ENDC}")
            print_info(f"Líneas totales: {complexity['total_loc']}")
            print_info(f"Promedio por archivo: {complexity['average_loc_per_file']:.0f}")
            
            if complexity.get('largest_file'):
                largest = complexity['largest_file']
                print_info(f"Archivo más grande: {largest['component']} "
                          f"({largest['lines_of_code']} líneas)")
            
            if complexity.get('most_classes'):
                most_cls = complexity['most_classes']
                print_info(f"Más clases: {most_cls['component']} "
                          f"({most_cls['count']} clases)")
            
            if complexity.get('most_functions'):
                most_funcs = complexity['most_functions']
                print_info(f"Más funciones: {most_funcs['component']} "
                          f"({most_funcs['count']} funciones)")
        
        except Exception as e:
            print_error(f"Error obteniendo estadísticas: {e}")
    
    def main_menu(self):
        """Menú principal"""
        while True:
            print_header()

            options = [
                f"{Symbols.GEAR} Asistente de Configuración",
                f"{Symbols.CHART} Analizar Codebase",
                f"{Symbols.ROBOT} Modo Interactivo (Gemini)",
                f"{Symbols.FOLDER} Ver Resumen del Sistema",
                f"{Symbols.SEARCH} Buscar en Código",
                f"{Symbols.CHART} Ver Estadísticas",
            ]

            print_menu(options)

            try:
                choice = input(f"{Colors.CYAN}{Symbols.ARROW} Opción: {Colors.ENDC}").strip()

                if choice == '0':
                    print()
                    print_info("¡Hasta luego! 👋")
                    sys.exit(0)
                elif choice == '1':
                    self.setup_wizard()
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass
                elif choice == '2':
                    self.analyze_codebase()
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass
                elif choice == '3':
                    self.interactive_query()
                elif choice == '4':
                    self.show_overview()
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass
                elif choice == '5':
                    self.search_code()
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass
                elif choice == '6':
                    self.show_stats()
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass
                else:
                    print_error("Opción no válida")
                    try:
                        input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                    except EOFError:
                        pass

            except KeyboardInterrupt:
                print()
                print_info("¡Hasta luego! 👋")
                sys.exit(0)
            except EOFError:
                # Handle non-interactive environments (like CI/CD or automated scripts)
                print()
                print_info("Modo no interactivo detectado. Ejecutando análisis automático...")
                self.analyze_codebase()
                print_info("¡Hasta luego! 👋")
                sys.exit(0)
            except Exception as e:
                print_error(f"Error: {e}")
                try:
                    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
                except EOFError:
                    pass

def main():
    """Punto de entrada principal"""
    try:
        cli = AiphaLabCLI()
        cli.main_menu()
    except KeyboardInterrupt:
        print()
        print_info("¡Hasta luego! 👋")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()