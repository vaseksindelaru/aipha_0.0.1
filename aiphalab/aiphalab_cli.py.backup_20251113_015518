#!/usr/bin/env python3
# aiphalab/aiphalab_cli.py
"""
AiphaLab - Interfaz CLI Profesional con Consulta Dual
Consulta Aipha_0.0.1 Y Aipha_1.0 simultáneamente

Versión: 3.1.0 (Multi-LLM Support)
Soporta: Gemini (Google) y Moonshot AI (Kimi)
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
import json
from datetime import datetime

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print_warning("python-dotenv no está instalado. Usa: pip install python-dotenv")

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
    AI = '🧠'  # LLM

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
    ║              🧠 Multi-LLM Support                         ║
    ║                   Versión 3.1.0                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.ENDC}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_section(title: str, system: str = "dual"):
    """Imprime título de sección con indicador de sistema"""
    icon = {
        'v0': f"{Symbols.V0} ",
        'v1': f"{Symbols.V1} ",
        'dual': f"{Symbols.DUAL} ",
        'ai': f"{Symbols.ROBOT} "
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

# ==================== LLM PROVIDERS ====================

class LLMProvider:
    """Interfaz genérica para proveedores LLM"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    def generate_content(self, prompt: str) -> str:
        raise NotImplementedError("Debe implementarse en subclases")
    
    def test_connection(self) -> tuple[bool, str]:
        """Prueba la conexión con el LLM"""
        try:
            response = self.generate_content("Say 'Hello World' in 5 words")
            return True, "Conexión exitosa"
        except Exception as e:
            return False, str(e)

class GeminiProvider(LLMProvider):
    """Proveedor para Google Gemini"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, model)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("google-generativeai no instalado. Usa: pip install google-generativeai")
    
    def generate_content(self, prompt: str) -> str:
        response = self.client.generate_content(prompt)
        return response.text

class MoonshotProvider(LLMProvider):
    """Proveedor para Moonshot AI (Kimi)"""
    
    def __init__(self, api_key: str, model: str = "kimi-k2-thinking"):
        super().__init__(api_key, model)
        try:
            import openai
            # Moonshot usa API compatible con OpenAI
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1"
            )
        except ImportError:
            raise ImportError("openai no instalado. Usa: pip install openai")
    
    def generate_content(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

# ==================== LLM FACTORY ====================

class LLMFactory:
    """Fábrica para crear el proveedor LLM configurado"""
    
    PROVIDERS = {
        "gemini": {
            "class": GeminiProvider,
            "env_key": "GEMINI_API_KEY",
            "default_model": "gemini-2.0-flash-exp"
        },
        "moonshot": {
            "class": MoonshotProvider,
            "env_key": "MOONSHOT_API_KEY",
            "default_model": "kimi-k2-thinking"
        }
    }
    
    @staticmethod
    def create_provider(provider_name: str, api_key: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
        """Crea una instancia del proveedor configurado"""
        if provider_name not in LLMFactory.PROVIDERS:
            raise ValueError(f"Proveedor '{provider_name}' no soportado. Opciones: {list(LLMFactory.PROVIDERS.keys())}")
        
        config = LLMFactory.PROVIDERS[provider_name]
        
        # Obtener API key
        if not api_key:
            api_key = os.getenv(config["env_key"])
            if not api_key:
                raise ValueError(
                    f"API key no encontrada para {provider_name}.\n"
                    f"Configura la variable de entorno: {config['env_key']}"
                )
        
        # Usar modelo personalizado o default
        model = model or config["default_model"]
        
        return config["class"](api_key, model)
    
    @staticmethod
    def get_available_providers() -> Dict[str, Any]:
        """Retorna proveedores disponibles con sus estados"""
        providers = {}
        for name, config in LLMFactory.PROVIDERS.items():
            api_key = os.getenv(config["env_key"])
            providers[name] = {
                "available": bool(api_key),
                "env_key": config["env_key"],
                "default_model": config["default_model"]
            }
        return providers


# ==================== CLASE PRINCIPAL CLI ====================

class AiphaLabCLI:
    """Interfaz CLI con consulta dual de proyectos y Multi-LLM"""
    
    def __init__(self):
        self.config_file = Path.home() / ".aiphalab" / "config.json"
        self.config = self.load_config()
        
        # Shadows para ambos sistemas
        self.shadow_v0 = None
        self.shadow_v1 = None
        
        # LLM providers para ambos sistemas
        self.llm_v0 = None
        self.llm_v1 = None
        
        # Bridge
        self.bridge = None
    
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración"""
        default_config = {
            'llm_provider': 'gemini',  # Proveedor por defecto
            'llm_model': None,  # Usará el modelo por defecto del proveedor
            'aipha_0_path': '/home/vaclav/Aipha_0.0.1',
            'aipha_1_path': '/home/vaclav/aipha_1'
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Mezclar con defaults para nuevas claves
                    return {**default_config, **saved_config}
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Guardar configuración"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def health_check(self) -> bool:
        """Verificación completa del sistema antes de usar LLM"""
        print_section("Verificación de Salud del Sistema", "ai")
        
        all_ok = True
        
        # 1. Verificar dependencias
        print_info("Verificando dependencias...")
        
        # Verificar dotenv
        try:
            import dotenv
            print_success("✓ python-dotenv instalado")
        except ImportError:
            print_warning("⚠️  python-dotenv no instalado (opcional pero recomendado)")
        
        # Verificar proveedor LLM
        provider_name = self.config.get('llm_provider', 'gemini')
        
        if provider_name == 'gemini':
            try:
                import google.generativeai
                print_success("✓ google-generativeai instalado")
            except ImportError:
                print_error("✗ google-generativeai no instalado")
                print_info("Instalar con: pip install google-generativeai")
                all_ok = False
        
        elif provider_name == 'moonshot':
            try:
                import openai
                print_success("✓ openai instalado (para Moonshot)")
            except ImportError:
                print_error("✗ openai no instalado")
                print_info("Instalar con: pip install openai")
                all_ok = False
        
        # 2. Verificar API key
        print_info(f"Verificando API key para {provider_name}...")
        
        try:
            provider = LLMFactory.create_provider(
                provider_name,
                self.config.get(f"{provider_name}_api_key"),
                self.config.get('llm_model')
            )
            
            # Probar conexión real
            success, message = provider.test_connection()
            if success:
                print_success(f"✓ API key válida y conexión exitosa")
            else:
                print_error(f"✗ Error de conexión: {message}")
                all_ok = False
                
        except Exception as e:
            print_error(f"✗ Error con API key: {str(e)}")
            all_ok = False
        
        # 3. Verificar rutas
        print_info("Verificando rutas de proyectos...")
        
        for version, path_key in [('v0', 'aipha_0_path'), ('v1', 'aipha_1_path')]:
            path = self.config.get(path_key)
            if Path(path).exists():
                print_success(f"✓ Ruta {version} válida: {path}")
            else:
                print_error(f"✗ Ruta {version} no existe: {path}")
                print_info(f"Configura correctamente en el asistente de configuración")
                all_ok = False
        
        # 4. Verificar componentes de Shadow
        print_info("Verificando componentes Shadow...")
        
        try:
            from hybrid import ShadowHybrid
            print_success("✓ hybrid disponible")
        except ImportError:
            print_error("✗ hybrid no encontrado")
            all_ok = False
        
        # Resumen
        print()
        if all_ok:
            print_success("🎉 Sistema listo para usar!")
        else:
            print_error("❌ Se encontraron problemas. Corrígelos antes de continuar.")
        
        return all_ok
    
    def setup_wizard(self):
        """Asistente de configuración mejorado con selección de LLM"""
        print_header()
        print_section("Asistente de Configuración Avanzada", "ai")
        
        # Mostrar proveedores disponibles
        print_info("Proveedores LLM disponibles:")
        providers = LLMFactory.get_available_providers()
        
        for name, info in providers.items():
            status = "✅ Configurado" if info["available"] else "❌ No configurado"
            print(f"  {Symbols.ROBOT} {name.capitalize()}: {status}")
            print(f"     Variable: {info['env_key']}")
            print(f"     Modelo: {info['default_model']}")
        
        print()
        
        # Elegir proveedor
        print(f"{Colors.BOLD}¿Qué proveedor LLM deseas usar?{Colors.ENDC}")
        provider_options = list(providers.keys()) + ["manual"]
        
        for i, provider in enumerate(provider_options, 1):
            status = "✅" if providers.get(provider, {}).get("available", False) else "❌"
            print(f"  {Colors.CYAN}{i}.{Colors.ENDC} {status} {provider.capitalize()}")
        
        print()
        
        provider_choice = input(f"{Colors.CYAN}Opción (1-{len(provider_options)}): {Colors.ENDC}").strip()
        
        try:
            provider_idx = int(provider_choice) - 1
            selected_provider = provider_options[provider_idx]
        except:
            print_error("Opción inválida, usando Gemini por defecto")
            selected_provider = "gemini"
        
        self.config['llm_provider'] = selected_provider
        
        # Configurar API key si no está en .env
        env_key = providers[selected_provider]["env_key"]
        current_key = os.getenv(env_key)
        
        if current_key:
            print_success(f"✓ API key encontrada en variables de entorno (***{current_key[-4:]})")
        else:
            print_info(f"API key no encontrada para {selected_provider}")
            new_key = input(f"{Colors.CYAN}{env_key}: {Colors.ENDC}").strip()
            if new_key:
                # Guardar en .env si existe el archivo
                env_file = Path(".env")
                if env_file.exists():
                    with open(env_file, "a") as f:
                        f.write(f"\n{env_key}={new_key}\n")
                    print_success(f"API key guardada en .env")
                else:
                    print_warning(f"Guarda esta clave: export {env_key}='{new_key}'")
                
                # También guardar en config por si acaso
                self.config[f"{selected_provider}_api_key"] = new_key
        
        # Elegir modelo específico (opcional)
        default_model = providers[selected_provider]["default_model"]
        model_input = input(f"{Colors.CYAN}Modelo [{default_model}]: {Colors.ENDC}").strip()
        self.config['llm_model'] = model_input if model_input else default_model
        
        # Configurar rutas
        print_section("Configuración de Rutas", "dual")
        
        # Aipha_0.0.1
        path_0 = input(f"{Colors.BLUE}Ruta Aipha_0.0.1 [{self.config.get('aipha_0_path')}]: {Colors.ENDC}").strip()
        if path_0:
            self.config['aipha_0_path'] = path_0
        
        if Path(self.config['aipha_0_path']).exists():
            print_success(f"✓ Aipha_0.0.1 encontrado")
        else:
            print_error(f"✗ Aipha_0.0.1 no encontrado")
        
        # Aipha_1.0
        path_1 = input(f"{Colors.GREEN}Ruta Aipha_1.0 [{self.config.get('aipha_1_path')}]: {Colors.ENDC}").strip()
        if path_1:
            self.config['aipha_1_path'] = path_1
        
        if Path(self.config['aipha_1_path']).exists():
            print_success(f"✓ Aipha_1.0 encontrado")
        else:
            print_warning(f"⚠️  Aipha_1.0 no encontrado (opcional)")
        
        self.save_config()
        
        # Ejecutar health check final
        print()
        print_info("Ejecutando verificación final...")
        if self.health_check():
            print()
            print_success("✨ Configuración completada exitosamente!")
        else:
            print()
            print_error("⚠️  Configuración guardada pero con problemas")
        
        return True
    
    def initialize_systems(self, system: str = "both", force_analysis: bool = False):
        """
        Inicializar sistemas con opción de análisis completo
        
        Args:
            system: "v0", "v1", o "both"
            force_analysis: Si True, hace análisis completo
        """
        # Verificar salud del sistema primero
        if not self.health_check():
            print_error("Sistema no está listo. Ejecuta la configuración primero.")
            return False
        
        try:
            # Inicializar Shadow Híbrido
            from hybrid import ShadowHybrid
            
            # Crear LLM provider según configuración
            provider_name = self.config.get('llm_provider', 'gemini')
            api_key = self.config.get(f"{provider_name}_api_key") or os.getenv(f"{provider_name.upper()}_API_KEY")
            model = self.config.get('llm_model')
            
            if system in ["v0", "both"] and self.shadow_v0 is None:
                print_system(f"Inicializando Aipha_0.0.1 con {provider_name}...", "v0")
                self.shadow_v0 = ShadowHybrid(self.config['aipha_0_path'])
                self.shadow_v0.analyze_codebase(force=force_analysis)
                
                # Crear LLM provider específico
                self.llm_v0 = LLMFactory.create_provider(provider_name, api_key, model)
                print_success("Aipha_0.0.1 listo")
            
            if system in ["v1", "both"] and self.shadow_v1 is None:
                print_system(f"Inicializando Aipha_1.0 con {provider_name}...", "v1")
                self.shadow_v1 = ShadowHybrid(self.config['aipha_1_path'])
                self.shadow_v1.analyze_codebase(force=force_analysis)
                
                # Crear LLM provider específico
                self.llm_v1 = LLMFactory.create_provider(provider_name, api_key, model)
                print_success("Aipha_1.0 listo")
            
            return True
        
        except ImportError as e:
            print_error(f"Error de importación: {e}")
            print_info("Instala las dependencias necesarias")
            return False
        except Exception as e:
            print_error(f"Error inicializando: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_bridge(self):
        """Inicializar puente (con soporte multi-LLM)"""
        if self.bridge is not None:
            return True
        
        try:
            from aipha_bridge import AiphaBridge
            print_info("Inicializando puente...")
            
            # Crear provider para el bridge
            provider_name = self.config.get('llm_provider', 'gemini')
            api_key = self.config.get(f"{provider_name}_api_key") or os.getenv(f"{provider_name.upper()}_API_KEY")
            model = self.config.get('llm_model')
            llm_provider = LLMFactory.create_provider(provider_name, api_key, model)
            
            self.bridge = AiphaBridge(
                self.config['aipha_0_path'],
                self.config['aipha_1_path'],
                llm_provider=llm_provider
            )
            
            # El bridge ya inicializa sus propios shadows
            self.shadow_v0 = self.bridge.shadow_v0
            self.shadow_v1 = self.bridge.shadow_v1
            self.llm_v1 = llm_provider
            
            print_success("Puente listo")
            return True
        
        except ImportError:
            print_warning("aipha_bridge no disponible. Usa opciones básicas.")
            return False
        except Exception as e:
            print_error(f"Error inicializando puente: {e}")
            return False
    
    def show_dual_overview(self):
        """Mostrar resumen de ambos sistemas"""
        print_section("Resumen Dual de Sistemas", "dual")
        
        if not self.initialize_systems("both", force_analysis=True):
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
            for comp in v0_overview.get('components', [])[:10]:
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
        
        print_system(f"Modo interactivo con {self.config['llm_provider']} iniciado", "v0")
        print_info("Escribe 'salir' para terminar")
        print()
        
        # Implementar modo interactivo básico
        while True:
            try:
                question = input(f"{Colors.BLUE}{Symbols.ROBOT} Pregunta: {Colors.ENDC}").strip()
                
                if question.lower() in ['salir', 'exit', 'quit']:
                    break
                
                if not question:
                    continue
                
                print(f"{Colors.CYAN}Consultando...{Colors.ENDC}")
                context = self.shadow_v0.get_context_for_llm()
                prompt = f"{context}\n\n=== PREGUNTA ===\n{question}"
                
                response = self.llm_v0.generate_content(prompt)
                print(f"\n{Colors.GREEN}{response}{Colors.ENDC}\n")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print_error(f"Error: {e}")
    
    def interactive_query_v1(self):
        """Modo interactivo con Aipha_1.0"""
        print_section("Modo Interactivo: Aipha_1.0", "v1")
        
        if not self.initialize_systems("v1"):
            return
        
        print_system(f"Modo interactivo con {self.config['llm_provider']} iniciado", "v1")
        print_info("Escribe 'salir' para terminar")
        print()
        
        # Implementar modo interactivo básico
        while True:
            try:
                question = input(f"{Colors.GREEN}{Symbols.ROBOT} Pregunta: {Colors.ENDC}").strip()
                
                if question.lower() in ['salir', 'exit', 'quit']:
                    break
                
                if not question:
                    continue
                
                print(f"{Colors.CYAN}Consultando...{Colors.ENDC}")
                context = self.shadow_v1.get_context_for_llm()
                prompt = f"{context}\n\n=== PREGUNTA ===\n{question}"
                
                response = self.llm_v1.generate_content(prompt)
                print(f"\n{Colors.GREEN}{response}{Colors.ENDC}\n")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print_error(f"Error: {e}")
    
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
            
            # Análisis con LLM
            print()
            analyze = input(f"{Colors.CYAN}¿Análisis detallado con {self.config['llm_provider']}? (s/n): {Colors.ENDC}").strip().lower()
            if analyze == 's':
                print()
                print_info(f"Consultando a {self.config['llm_provider']}...")
                
                context = self.shadow_v0.get_context_for_llm(component) + "\n" + \
                         self.shadow_v1.get_context_for_llm(component)
                
                analysis_prompt = f"{context}\n\nAnaliza la evolución de '{component}' entre versiones."
                response = self.llm_v0.generate_content(analysis_prompt)
                
                print()
                print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
                print(response)
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
            response = ""
            if choice == '1':
                print_info("Generando guía de ATR...")
                guide = self.bridge.get_atr_learning_guide()
                response = guide
            
            elif choice == '2':
                print_info("Analizando integración PCE + ATR...")
                analysis = self.bridge.analyze_pce_atr_integration()
                response = analysis
            
            elif choice == '3':
                print_info("Buscando archivos de Capa 1...")
                files = self.bridge.search_layer1_components()
                print()
                print(f"{Colors.BOLD}Archivos encontrados: {len(files)}{Colors.ENDC}\n")
                for f in files[:15]:
                    print(f"  {Colors.GREEN}{Symbols.FILE}{Colors.ENDC} {f}")
                return  # No hay respuesta para guardar
            
            elif choice == '4':
                component = input(f"{Colors.CYAN}Componente a implementar: {Colors.ENDC}").strip()
                if component:
                    print()
                    print_info(f"Generando roadmap para '{component}'...")
                    roadmap = self.bridge.get_implementation_roadmap(component)
                    response = roadmap
            
            elif choice == '5':
                topic = input(f"{Colors.CYAN}¿Sobre qué quieres aprender?: {Colors.ENDC}").strip()
                if topic:
                    print()
                    print_info(f"Consultando sobre '{topic}'...")
                    insights = self.bridge.get_quick_insights(topic)
                    response = insights
            
            else:
                print_error("Opción inválida")
                return
            
            # Mostrar y guardar respuesta
            if response:
                print()
                print(response)
                print()
                
                save = input(f"{Colors.CYAN}¿Guardar respuesta? (s/n): {Colors.ENDC}").strip().lower()
                if save == 's':
                    filename = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# AiphaLab - Sesión de Aprendizaje ({self.config['llm_provider']})\n\n")
                        f.write(response)
                    print_success(f"Guardado en: {filename}")
        
        except Exception as e:
            print_error(f"Error: {e}")
    
    def view_current_config(self):
        """Ver configuración actual"""
        print_section("Configuración Actual", "ai")
        
        print_info(f"Proveedor LLM: {self.config.get('llm_provider', 'No configurado')}")
        print_info(f"Modelo: {self.config.get('llm_model', 'Default')}")
        
        provider_name = self.config.get('llm_provider', 'gemini')
        env_key = LLMFactory.PROVIDERS[provider_name]["env_key"]
        api_key = os.getenv(env_key) or self.config.get(f"{provider_name}_api_key")
        
        if api_key:
            print_success(f"API key: ***{api_key[-4:]} (configurada)")
        else:
            print_error("API key: No configurada")
        
        print()
        print_info(f"Aipha_0.0.1: {self.config.get('aipha_0_path')}")
        print_info(f"Aipha_1.0: {self.config.get('aipha_1_path')}")
        
        # Verificar rutas
        for version, path_key in [('v0', 'aipha_0_path'), ('v1', 'aipha_1_path')]:
            path = self.config.get(path_key)
            if Path(path).exists():
                print_success(f"✓ Ruta {version} existe")
            else:
                print_error(f"✗ Ruta {version} no existe")
        
        input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
    
    def main_menu(self):
        """Menú principal mejorado"""
        while True:
            print_header()
            
            current_provider = self.config.get('llm_provider', 'No configurado')
            
            options = [
                f"{Symbols.GEAR} Configuración Inicial / Cambiar LLM",
                f"{Symbols.ROBOT} Ver Configuración Actual (LLM: {current_provider})",
                f"{Symbols.DUAL} Verificar Salud del Sistema",
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
                    self.view_current_config()
                
                elif choice == '3':
                    self.health_check()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                
                elif choice == '4':
                    self.show_dual_overview()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                
                elif choice in ['5', '6', '7', '9']:  # Opciones que usan LLM
                    # Verificar salud antes de permitir
                    if not self.health_check():
                        print_warning("Corrige los problemas antes de continuar")
                        input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                        continue
                    
                    if choice == '5':
                        self.interactive_query_v0()
                    elif choice == '6':
                        self.interactive_query_v1()
                    elif choice == '7':
                        self.compare_component()
                        input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                    elif choice == '9':
                        self.learn_from_v1()
                        input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                
                elif choice == '8':
                    self.search_in_system()
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                
                elif choice == '10':
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
                print()
                print_info("Modo no interactivo detectado. Ejecutando análisis automático...")
                if self.initialize_systems("both"):
                    self.show_dual_overview()
                print_info("¡Hasta luego! 👋")
                sys.exit(0)
            except Exception as e:
                print_error(f"Error inesperado: {e}")
                import traceback
                traceback.print_exc()
                try:
                    input(f"\n{Colors.CYAN}Presiona Enter...{Colors.ENDC}")
                except EOFError:
                    pass


def main():
    """Punto de entrada"""
    try:
        cli = AiphaLabCLI()
        
        # Si no hay configuración, forzar asistente
        if not cli.config.get('llm_provider') or not cli.health_check():
            print_warning("Configuración incompleta o inválida. Iniciando asistente...")
            if not cli.setup_wizard():
                print_error("No se pudo completar la configuración")
                sys.exit(1)
        
        cli.main_menu()
    
    except KeyboardInterrupt:
        print()
        print_info("¡Hasta luego! 👋")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()