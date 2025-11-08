#!/usr/bin/env python3
# aiphalab/aiphalab_cli.py
"""
AiphaLab - Interfaz CLI Profesional con Consulta Dual
Consulta Aipha_0.0.1 Y Aipha_1.0 simultáneamente

Versión: 3.0.0 (Dual System)
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Colores y símbolos
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    BRIDGE = '🌉'
    BOOK = '📚'
    LIGHTBULB = '💡'
    V0 = '🔵'  # Aipha_0.0.1
    V1 = '🟢'  # Aipha_1.0
    DUAL = '🔄'  # Ambos

def print_header():
    """Header con diseño dual"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print(r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║     █████╗ ██╗██████╗ ██╗  ██╗ █████╗ ██╗      █████╗   ║
    ║    ██╔══██╗██║██╔══██╗██║  ██║██╔══██╗██║     ██╔══██╗  ║
    ║    ███████║██║██████╔╝███████║███████║██║     ███████║  ║
    ║    ██╔══██║██║██╔═══╝ ██╔══██║██╔══██║██║     ██╔══██║  ║
    ║    ██║  ██║██║██║     ██║  ██║██║  ██║███████╗██║  ██║  ║
    ║    ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ║
    ║                                                           ║
    ║         🔵 AIPHA_0.0.1  🔄  AIPHA_1.0 🟢                 ║
    ║              Consulta Dual de Proyectos                  ║
    ║                   Versión 3.0.0                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_section(title: str, system: str = "dual"):
    """Imprime título de sección con indicador de sistema"""
    icon = {
        'v0': f"{Symbols.V0} ",
        'v1': f"{Symbols.V1} ",
        'dual': f"{Symbols.DUAL} "
    }.get(system, "")
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{icon}{Symbols.ARROW} {title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.ENDC}\n")

def print_success(message: str):
    print(f"{Colors.GREEN}{Symbols.CHECK} {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}{Symbols.CROSS} {message}{Colors.ENDC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message: str):
    print(f"{Colors.CYAN}{Symbols.BULLET} {message}{Colors.ENDC}")

def print_system(message: str, system: str = "v0"):
    """Print con indicador de sistema"""
    color = Colors.BLUE if system == "v0" else Colors.GREEN
    icon = Symbols.V0 if system == "v0" else Symbols.V1
    print(f"{color}{icon} {message}{Colors.ENDC}")

def print_menu(options: list):
    """Imprime menú"""
    print(f"\n{Colors.BOLD}Selecciona una opción:{Colors.ENDC}\n")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.CYAN}{i:2d}.{Colors.ENDC} {option}")
    print(f"\n  {Colors.CYAN} 0.{Colors.ENDC} {Colors.RED}Salir{Colors.ENDC}")
    print()


class AiphaLabCLI:
    """Interfaz CLI con consulta dual de proyectos"""
    
    def __init__(self):
        self.config_file = Path.home() / ".aiphalab" / "config.json"
        self.config = self.load_config()
        
        # Shadows para ambos sistemas
        self.shadow_v0 = None  # Aipha_0.0.1
        self.shadow_v1 = None  # Aipha_1.0
        
        # Gemini para ambos sistemas
        self.gemini_v0 = None
        self.gemini_v1 = None
        
        # Bridge
        self.bridge = None
        
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'aipha_0_path': '../Aipha_0.0.1',
            'aipha_1_path': '/home/vaclav/aipha_1'
        }
    
    def save_config(self):
        """Guardar configuración"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_wizard(self):
        """Asistente de configuración"""
        print_header()
        print_section("Asistente de Configuración", "dual")
        
        # Verificar API key
        print_info("Verificando API key...")
        if os.getenv('GEMINI_API_KEY'):
            key = os.getenv('GEMINI_API_KEY')
            print_success(f"GEMINI_API_KEY configurada (***{key[-4:]})")
        else:
            print_error("GEMINI_API_KEY no configurada")
            print_warning("export GEMINI_API_KEY='tu_key'")
            return False
        
        # Configurar Aipha_0.0.1
        print()
        print_system("Configurando Aipha_0.0.1...", "v0")
        path_0 = input(f"{Colors.BLUE}Ruta [{self.config.get('aipha_0_path')}]: {Colors.ENDC}").strip()
        if path_0:
            self.config['aipha_0_path'] = path_0
        
        if Path(self.config['aipha_0_path']).exists():
            print_success(f"Encontrado: {self.config['aipha_0_path']}")
        else:
            print_error(f"No encontrado: {self.config['aipha_0_path']}")
        
        # Configurar Aipha_1.0
        print()
        print_system("Configurando Aipha_1.0...", "v1")
        path_1 = input(f"{Colors.GREEN}Ruta [{self.config.get('aipha_1_path')}]: {Colors.ENDC}").strip()
        if path_1:
            self.config['aipha_1_path'] = path_1
        
        if Path(self.config['aipha_1_path']).exists():
            print_success(f"Encontrado: {self.config['aipha_1_path']}")
        else:
            print_warning(f"No encontrado: {self.config['aipha_1_path']}")
        
        self.save_config()
        print()
        print_success("✨ Configuración completada!")
        return True
    
    def initialize_systems(self, system: str = "both"):
        """
        Inicializar sistemas
        
        Args:
            system: "v0", "v1", o "both"
        """
        try:
            from shadow_hybrid import ShadowHybrid
            from gemini_integration import GeminiShadow
            
            if system in ["v0", "both"] and self.shadow_v0 is None:
                print_system("Inicializando Aipha_0.0.1...", "v0")
                self.shadow_v0 = ShadowHybrid(self.config['aipha_0_path'])
                self.shadow_v0.analyze_codebase(force=False)
                self.gemini_v0 = GeminiShadow(base_path=self.config['aipha_0_path'])
                print_success("Aipha_0.0.1 listo")
            
            if system in ["v1", "both"] and self.shadow_v1 is None:
                print_system("Inicializando Aipha_1.0...", "v1")
                self.shadow_v1 = ShadowHybrid(self.config['aipha_1_path'])
                self.shadow_v1.analyze_codebase(force=False)
                self.gemini_v1 = GeminiShadow(base_path=self.config['aipha_1_path'])
                print_success("Aipha_1.0 listo")
            
            return True
        
        except Exception as e:
            print_error(f"Error inicializando: {e}")
            return False
    
    def initialize_bridge(self):
        """Inicializar puente"""
        if self.bridge is not None:
            return True
        
        try:
            from aipha_bridge import AiphaBridge
            print_info("Inicializando puente...")
            self.bridge = AiphaBridge(
                self.config['aipha_0_path'],
                self.config['aipha_1_path']
            )
            # El bridge ya inicializa sus propios shadows
            self.shadow_v0 = self.bridge.shadow_v0
            self.shadow_v1 = self.bridge.shadow_v1
            self.gemini_v1 = self.bridge.gemini
            print_success("Puente listo")
            return True
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def show_dual_overview(self):
        """Mostrar resumen de ambos sistemas"""
        print_section("Resumen Dual de Sistemas", "dual")
        
        if not self.initialize_systems("both"):
            return
        
        try:
            v0_overview = self.shadow_v0.get_system_overview()
            v1_overview = self.shadow_v1.get_system_overview()
            
            # Tabla comparativa
            print(f"{Colors.BOLD}{'Sistema':<20} {'Componentes':<15} {'Entradas':<15}{Colors.ENDC}")
            print(f"{Colors.BLUE}{'─'*50}{Colors.ENDC}")
            print(f"{Colors.BLUE}{Symbols.V0} Aipha_0.0.1{' '*7}{v0_overview['total_components']:<15} {v0_overview['total_entries']:<15}{Colors.ENDC}")
            print(f"{Colors.GREEN}{Symbols.V1} Aipha_1.0{' '*9}{v1_overview['total_components']:<15} {v1_overview['total_entries']:<15}{Colors.ENDC}")
            print(f"{Colors.BLUE}{'─'*50}{Colors.ENDC}")
            
            ratio = v1_overview['total_components'] / max(v0_overview['total_components'], 1)
            print()
            print_info(f"Aipha_1.0 es {ratio:.1f}x más complejo")
            print_info(f"Diferencia: {v1_overview['total_components'] - v0_overview['total_components']} componentes")
            
            # Componentes únicos
            print()
            print(f"{Colors.BOLD}Componentes de Aipha_0.0.1:{Colors.ENDC}")
            for comp in v0_overview.get('components', []):
                print(f"  {Colors.BLUE}{Symbols.FILE}{Colors.ENDC} {comp}")
            
            print()
            print(f"{Colors.BOLD}Primeros 10 componentes de Aipha_1.0:{Colors.ENDC}")
            for comp in v1_overview.get('components', [])[:10]:
                print(f"  {Colors.GREEN}{Symbols.FILE}{Colors.ENDC} {comp}")
            
            if len(v1_overview.get('components', [])) > 10:
                print_info(f"... y {len(v1_overview['components']) - 10} más")
        
        except Exception as e:
            print_error(f"Error: {e}")
    
    def interactive_query_v0(self):
        """Modo interactivo con Aipha_0.0.1"""
        print_section("Modo Interactivo: Aipha_0.0.1", "v0")
        
        if not self.initialize_systems("v0"):
            return
        
        print_system("Modo interactivo iniciado", "v0")
        print_info("Escribe 'salir' para terminar")
        print()
        
        self.gemini_v0.interactive_mode()
    
    def interactive_query_v1(self):
        """Modo interactivo con Aipha_1.0"""
        print_section("Modo Interactivo: Aipha_1.0", "v1")
        
        if not self.initialize_systems("v1"):
            return
        
        print_system("Modo interactivo iniciado", "v1")
        print_info("Escribe 'salir' para terminar")
        print()
        
        self.gemini_v1.interactive_mode()
    
    def compare_component(self):
        """Comparar componente entre versiones"""
        print_section("Comparación de Componente", "dual")
        
        if not self.initialize_bridge():
            return
        
        component = input(f"{Colors.CYAN}Componente a comparar (ej: potential_capture_engine): {Colors.ENDC}").strip()
        if not component:
            return
        
        print()
        print_info(f"Comparando '{component}'...")
        
        try:
            comparison = self.bridge.compare_component(component)
            
            # Mostrar V0
            print()
            print_system(f"Aipha_0.0.1: {comparison['v0']['file']}", "v0")
            if comparison['v0']['exists']:
                details = comparison['v0']['details']
                print(f"  Clases: {len(details.get('classes', []))}")
                print(f"  Funciones: {len(details.get('functions', []))}")
                print(f"  LOC: {details.get('lines_of_code', 0)}")
            else:
                print_warning("  No existe en v0")
            
            # Mostrar V1
            print()
            print_system(f"Aipha_1.0: {comparison['v1']['file']}", "v1")
            if comparison['v1']['exists']:
                details = comparison['v1']['details']
                print(f"  Clases: {len(details.get('classes', []))}")
                print(f"  Funciones: {len(details.get('functions', []))}")
                print(f"  LOC: {details.get('lines_of_code', 0)}")
            else:
                print_warning("  No existe en v1")
            
            # Evolución
            if 'evolution' in comparison:
                print()
                print(f"{Colors.BOLD}Evolución:{Colors.ENDC}")
                evo = comparison['evolution']
                print_info(f"Clases agregadas: {evo['classes_added']}")
                print_info(f"Funciones agregadas: {evo['functions_added']}")
                print_info(f"LOC crecimiento: {evo['loc_growth']}")
            
            # Análisis con Gemini
            print()
            analyze = input(f"{Colors.CYAN}¿Análisis detallado con Gemini? (s/n): {Colors.ENDC}").strip().lower()
            if analyze == 's':
                print()
                print_info("Consultando a Gemini...")
                analysis = self.bridge.explain_component_evolution(component)
                print()
                print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
                print(analysis)
                print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
        
        except Exception as e:
            print_error(f"Error: {e}")
    
    def search_in_system(self):
        """Buscar en sistema específico"""
        print_section("Búsqueda en Sistema", "dual")
        
        print(f"{Colors.BOLD}¿En qué sistema buscar?{Colors.ENDC}\n")
        print(f"  {Colors.BLUE}1.{Colors.ENDC} {Symbols.V0} Aipha_0.0.1")
        print(f"  {Colors.GREEN}2.{Colors.ENDC} {Symbols.V1} Aipha_1.0")
        print(f"  {Colors.CYAN}3.{Colors.ENDC} {Symbols.DUAL} Ambos")
        print()
        
        choice = input(f"{Colors.CYAN}Opción: {Colors.ENDC}").strip()
        
        keyword = input(f"{Colors.CYAN}Término a buscar: {Colors.ENDC}").strip()
        if not keyword:
            return
        
        print()
        
        if choice in ['1', '3']:
            if self.initialize_systems("v0"):
                print_system(f"Búsqueda en Aipha_0.0.1: '{keyword}'", "v0")
                results = self.shadow_v0.search(keyword, search_type='hybrid')
                print_info(f"Coincidencias texto: {len(results.get('text_matches', []))}")
                print_info(f"Coincidencias estructurales: {len(results.get('structural_matches', []))}")
                
                if results.get('structural_matches'):
                    print()
                    for match in results['structural_matches'][:5]:
                        print(f"  {Colors.BLUE}{match['type']}:{Colors.ENDC} {match['name']} en {match['component']}")
        
        if choice in ['2', '3']:
            if choice == '3':
                print()
            
            if self.initialize_systems("v1"):
                print_system(f"Búsqueda en Aipha_1.0: '{keyword}'", "v1")
                results = self.shadow_v1.search(keyword, search_type='hybrid')
                print_info(f"Coincidencias texto: {len(results.get('text_matches', []))}")
                print_info(f"Coincidencias estructurales: {len(results.get('structural_matches', []))}")
                
                if results.get('structural_matches'):
                    print()
                    for match in results['structural_matches'][:5]:
                        print(f"  {Colors.GREEN}{match['type']}:{Colors.ENDC} {match['name']} en {match['component']}")
    
    def learn_from_v1(self):
        """Aprender de Aipha_1.0"""
        print_section("Aprender de Aipha_1.0", "v1")
        
        if not self.initialize_bridge():
            return
        
        print(f"{Colors.BOLD}Temas disponibles:{Colors.ENDC}\n")
        print("  1. ATR (Average True Range)")
        print("  2. Integración PCE + ATR")
        print("  3. Capa 1 (Layer 1)")
        print("  4. Roadmap de implementación")
        print("  5. Consulta libre")
        print()
        
        choice = input(f"{Colors.CYAN}Opción: {Colors.ENDC}").strip()
        
        print()
        
        try:
            if choice == '1':
                print_info("Generando guía de ATR...")
                guide = self.bridge.get_atr_learning_guide()
                print()
                print(guide)
            
            elif choice == '2':
                print_info("Analizando integración PCE + ATR...")
                analysis = self.bridge.analyze_pce_atr_integration()
                print()
                print(analysis)
            
            elif choice == '3':
                print_info("Buscando archivos de Capa 1...")
                files = self.bridge.search_layer1_components()
                print()
                print(f"{Colors.BOLD}Archivos encontrados: {len(files)}{Colors.ENDC}\n")
                for f in files[:15]:
                    print(f"  {Colors.GREEN}{Symbols.FILE}{Colors.ENDC} {f}")
            
            elif choice == '4':
                component = input(f"{Colors.CYAN}Componente a implementar: {Colors.ENDC}").strip()
                if component:
                    print()
                    print_info(f"Generando roadmap para '{component}'...")
                    roadmap = self.bridge.get_implementation_roadmap(component)
                    print()
                    print(roadmap)
            
            elif choice == '5':
                topic = input(f"{Colors.CYAN}¿Sobre qué quieres aprender?: {Colors.ENDC}").strip()
                if topic:
                    print()
                    print_info(f"Consultando sobre '{topic}'...")
                    insights = self.bridge.get_quick_insights(topic)
                    print()
                    print(insights)
            
            # Opción de guardar
            if choice in ['1', '2', '4', '5']:
                print()
                save = input(f"{Colors.CYAN}¿Guardar respuesta? (s/n): {Colors.ENDC}").strip().lower()
                if save == 's':
                    filename = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("# AiphaLab - Sesión de Aprendizaje\n\n")
                        if choice == '1':
                            f.write(guide)
                        elif choice == '2':
                            f.write(analysis)
                        elif choice == '4':
                            f.write(roadmap)
                        elif choice == '5':
                            f.write(insights)
                    print_success(f"Guardado en: {filename}")
        
        except Exception as e:
            print_error(f"Error: {e}")
    
    def main_menu(self):
        """Menú principal"""
        while True:
            print_header()
            
            options = [
                f"{Symbols.GEAR} Configuración Inicial",
                f"{Symbols.DUAL} Resumen Dual (v0 + v1)",
                f"{Symbols.V0} Consultar Aipha_0.0.1 (interactivo)",
                f"{Symbols.V1} Consultar Aipha_1.0 (interactivo)",
                f"{Symbols.DUAL} Comparar Componente",
                f"{Symbols.SEARCH} Buscar en Sistemas",
                f"{Symbols.BOOK} Aprender de Aipha_1.0",
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
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                elif choice == '2':
                    self.show_dual_overview()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                elif choice == '3':
                    self.interactive_query_v0()
                elif choice == '4':
                    self.interactive_query_v1()
                elif choice == '5':
                    self.compare_component()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                elif choice == '6':
                    self.search_in_system()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                elif choice == '7':
                    self.learn_from_v1()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                elif choice == '8':
                    # Mostrar stats de ambos sistemas
                    if self.initialize_systems("both"):
                        print_section("Estadísticas", "dual")
                        print_system("Aipha_0.0.1:", "v0")
                        print(self.shadow_v0.format_for_display(
                            self.shadow_v0.get_system_overview()))
                        print()
                        print_system("Aipha_1.0:", "v1")
                        print(self.shadow_v1.format_for_display(
                            self.shadow_v1.get_system_overview()))
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                else:
                    print_error("Opción no válida")
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
            
            except KeyboardInterrupt:
                print()
                print_info("¡Hasta luego! 👋")
                sys.exit(0)
            except EOFError:
                # Handle non-interactive environments
                print()
                print_info("Modo no interactivo detectado. Ejecutando análisis automático...")
                if self.initialize_systems("both"):
                    self.show_dual_overview()
                print_info("¡Hasta luego! 👋")
                sys.exit(0)
            except Exception as e:
                print_error(f"Error: {e}")
                try:
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                except EOFError:
                    pass


def main():
    """Punto de entrada"""
    try:
        cli = AiphaLabCLI()
        cli.main_menu()
    except KeyboardInterrupt:
        print()
        print_info("¡Hasta luego! 👋")
        sys.exit(0)

if __name__ == "__main__":
    main()