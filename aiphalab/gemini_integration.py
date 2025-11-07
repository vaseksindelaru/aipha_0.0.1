# aiphalab/gemini_integration.py
"""
Integración de Gemini con Shadow Híbrido
Permite a Gemini consultar su propio contexto (Aipha_0.0.1) de forma inteligente

CARACTERÍSTICAS:
- Integración con Shadow Híbrido (análisis + MCPs)
- Contexto inteligente y adaptativo
- Modo interactivo para exploración
- Cache de consultas para eficiencia
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# Verificar disponibilidad de Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Warning: google-generativeai no está instalado")
    print("   Instalar con: pip install google-generativeai")

# Importar Shadow (intentar híbrido primero, fallback a query)
try:
    from shadow_hybrid import ShadowHybrid
    SHADOW_HYBRID_AVAILABLE = True
except ImportError:
    SHADOW_HYBRID_AVAILABLE = False
    try:
        from shadow_query import ShadowQuery
        print("ℹ️  Usando ShadowQuery (modo básico)")
    except ImportError:
        raise ImportError("No se encontró ni shadow_hybrid ni shadow_query")


class GeminiShadow:
    """
    Integración inteligente entre Gemini y Shadow.
    Permite a Gemini consultar su propio contexto (Aipha_0.0.1) de forma eficiente.
    
    VENTAJAS DE VERSIÓN HÍBRIDA:
    - Análisis incremental (10-100x más rápido)
    - Búsqueda ultrarrápida con ripgrep
    - Cache inteligente con SQLite
    - Contexto rico con historial Git
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 base_path: str = "../Aipha_0.0.1",
                 model: str = "gemini-2.0-flash-exp"):
        """
        Inicializar GeminiShadow
        
        Args:
            api_key: API key de Google Gemini (opcional, puede usar env var)
            base_path: Ruta al código de Aipha_0.0.1
            model: Modelo de Gemini a usar
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai no está instalado")
        
        # Configurar Gemini
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key no proporcionada.\n"
                "Use: api_key parameter o GEMINI_API_KEY env var"
            )
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        
        # Inicializar Shadow (híbrido si está disponible)
        if SHADOW_HYBRID_AVAILABLE:
            print("[GeminiShadow] Inicializando Shadow Híbrido...")
            self.shadow = ShadowHybrid(base_path)
            self.shadow_mode = "hybrid"
        else:
            print("[GeminiShadow] Inicializando Shadow Query (básico)...")
            from shadow_query import ShadowQuery
            self.shadow = ShadowQuery()
            self.shadow_mode = "basic"
        
        # Cache de conversación
        self.conversation_history = []
        
        # Estadísticas
        self.stats = {
            'queries': 0,
            'cache_hits': 0,
            'errors': 0
        }
        
        print(f"[GeminiShadow] ✅ Inicializado correctamente")
        print(f"[GeminiShadow] Modelo: {model}")
        print(f"[GeminiShadow] Shadow Mode: {self.shadow_mode}")
        
        # Analizar código si es Shadow Híbrido
        if self.shadow_mode == "hybrid":
            print("[GeminiShadow] Analizando codebase...")
            self.shadow.analyze_codebase(force=False)
        
        # Cargar contexto inicial
        self._load_system_context()
    
    def _load_system_context(self):
        """Cargar contexto del sistema en memoria"""
        try:
            if self.shadow_mode == "hybrid":
                self.system_context = self.shadow.get_context_for_llm()
            else:
                self.system_context = self.shadow.get_context_for_gemini()
            
            components_count = len(self.shadow.get_all_components() if hasattr(self.shadow, 'get_all_components') 
                                  else self.shadow.core.get_all_components())
            
            print(f"[GeminiShadow] Contexto cargado: {components_count} componentes")
        except Exception as e:
            print(f"[GeminiShadow] Error cargando contexto: {e}")
            self.system_context = "Contexto no disponible"
    
    def _build_system_prompt(self) -> str:
        """Construye el system prompt para Gemini"""
        return f"""Eres un asistente de IA especializado en el sistema Aipha_0.0.1.
Tienes acceso completo al código y estructura del sistema a través de Shadow.

Tu propósito es:
1. Explicar la arquitectura y funcionamiento de Aipha_0.0.1
2. Responder preguntas sobre clases, funciones y componentes
3. Analizar relaciones y dependencias entre componentes
4. Proporcionar insights sobre la estructura del código

Capacidades especiales:
- Puedes ver toda la estructura del código
- Entiendes las relaciones entre componentes
- Conoces el propósito de cada clase y función
- Puedes hacer análisis arquitectónico

IMPORTANTE:
- Basa tus respuestas en el contexto proporcionado
- Si algo no está en el contexto, indícalo claramente
- Sé específico y técnico cuando sea necesario
- Proporciona ejemplos cuando ayude a la comprensión"""
    
    def _build_prompt_with_context(self, user_question: str, 
                                   focus_component: Optional[str] = None) -> str:
        """
        Construye un prompt completo con contexto
        
        Args:
            user_question: Pregunta del usuario
            focus_component: Componente específico para contexto enfocado
        
        Returns:
            Prompt completo con contexto
        """
        # Contexto específico si se solicita
        if focus_component:
            if self.shadow_mode == "hybrid":
                context = self.shadow.get_context_for_llm(focus=focus_component)
            else:
                context = self.shadow.get_context_for_gemini(focus=focus_component)
        else:
            context = self.system_context
        
        prompt = f"""{self._build_system_prompt()}

=== CONTEXTO DEL SISTEMA AIPHA_0.0.1 ===
{context}

=== PREGUNTA DEL USUARIO ===
{user_question}

Por favor, responde basándote en el contexto del sistema proporcionado."""
        
        return prompt
    
    def ask(self, question: str, 
            focus_component: Optional[str] = None,
            use_history: bool = True) -> str:
        """
        Hacer una pregunta a Gemini con contexto de Shadow
        
        Args:
            question: Pregunta sobre el sistema
            focus_component: Enfocar contexto en un componente específico
            use_history: Usar historial de conversación
        
        Returns:
            Respuesta de Gemini
        """
        try:
            self.stats['queries'] += 1
            
            # Construir prompt con contexto
            prompt = self._build_prompt_with_context(question, focus_component)
            
            # Agregar historial si se requiere
            if use_history and self.conversation_history:
                history_text = "\n\n=== CONVERSACIÓN PREVIA ===\n"
                for entry in self.conversation_history[-3:]:  # Últimas 3 interacciones
                    history_text += f"Usuario: {entry['question']}\n"
                    history_text += f"Asistente: {entry['answer'][:200]}...\n\n"
                prompt = history_text + prompt
            
            # Consultar Gemini
            response = self.model.generate_content(prompt)
            answer = response.text
            
            # Guardar en historial
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'answer': answer,
                'focus_component': focus_component
            })
            
            return answer
        
        except Exception as e:
            self.stats['errors'] += 1
            error_msg = f"Error al consultar Gemini: {str(e)}"
            print(f"[GeminiShadow] {error_msg}")
            return error_msg
    
    def ask_about_component(self, component_name: str) -> str:
        """
        Análisis detallado de un componente específico
        
        Args:
            component_name: Nombre del componente (archivo)
        
        Returns:
            Análisis de Gemini
        """
        # Verificar que el componente existe
        if self.shadow_mode == "hybrid":
            details = self.shadow.get_component_details(component_name)
        else:
            details = self.shadow.get_component_details(component_name)
        
        if not details:
            return f"❌ Componente '{component_name}' no encontrado en Shadow"
        
        question = f"""Analiza el componente '{component_name}' en detalle:

1. ¿Cuál es su propósito principal?
2. ¿Qué clases y funciones principales contiene?
3. ¿Cómo se relaciona con otros componentes?
4. ¿Cuáles son sus dependencias clave?
5. ¿Hay algo notable en su implementación?"""
        
        return self.ask(question, focus_component=component_name)
    
    def get_architecture_explanation(self) -> str:
        """
        Explicación completa de la arquitectura del sistema
        
        Returns:
            Análisis arquitectónico detallado
        """
        question = """Basándote en el contexto completo del sistema, proporciona un análisis arquitectónico:

1. **Arquitectura General**: ¿Cómo está organizado Aipha_0.0.1?
2. **Componentes Principales**: ¿Cuáles son los componentes clave y qué hace cada uno?
3. **Flujo de Ejecución**: ¿Cómo fluyen los datos y el control?
4. **Patrones de Diseño**: ¿Qué patrones arquitectónicos identificas?
5. **Relaciones**: ¿Cómo interactúan los componentes entre sí?

Sé específico y usa ejemplos del código."""
        
        return self.ask(question, use_history=False)
    
    def search_and_explain(self, keyword: str) -> str:
        """
        Buscar un término y explicar su uso en el sistema
        
        Args:
            keyword: Término a buscar
        
        Returns:
            Explicación contextualizada
        """
        # Buscar usando Shadow
        if self.shadow_mode == "hybrid":
            results = self.shadow.search(keyword, search_type='hybrid')
            
            # Formatear resultados
            search_summary = f"Búsqueda de '{keyword}':\n"
            search_summary += f"- Coincidencias de texto: {len(results.get('text_matches', []))}\n"
            search_summary += f"- Coincidencias estructurales: {len(results.get('structural_matches', []))}\n"
            
            if results.get('structural_matches'):
                search_summary += "\nCoincidencias estructurales:\n"
                for match in results['structural_matches'][:5]:
                    search_summary += f"- {match['type']}: {match['name']} en {match['component']}\n"
        else:
            results = self.shadow.search_by_keyword(keyword)
            search_summary = f"Búsqueda de '{keyword}': {len(results)} resultados encontrados\n"
        
        question = f"""He encontrado '{keyword}' en el código:

{search_summary}

Por favor explica:
1. ¿Qué es/representa '{keyword}' en el contexto de Aipha_0.0.1?
2. ¿Dónde y cómo se usa?
3. ¿Cuál es su importancia en el sistema?"""
        
        return self.ask(question)
    
    def compare_components(self, component1: str, component2: str) -> str:
        """
        Comparar dos componentes del sistema
        
        Args:
            component1: Primer componente
            component2: Segundo componente
        
        Returns:
            Análisis comparativo
        """
        question = f"""Compara los componentes '{component1}' y '{component2}':

1. ¿Qué tienen en común?
2. ¿En qué se diferencian?
3. ¿Cómo se relacionan entre sí?
4. ¿Cuál es el rol de cada uno en el sistema?"""
        
        return self.ask(question)
    
    def analyze_dependencies(self, component: str) -> str:
        """
        Analizar las dependencias de un componente
        
        Args:
            component: Nombre del componente
        
        Returns:
            Análisis de dependencias
        """
        # Obtener dependencias
        if self.shadow_mode == "hybrid":
            deps = self.shadow.shadow.core.get_component_analysis(component)
        else:
            deps = self.shadow.get_dependencies(component)
        
        question = f"""Analiza las dependencias del componente '{component}':

Dependencias encontradas: {deps}

1. ¿Qué librerías/módulos externos usa?
2. ¿Qué componentes internos necesita?
3. ¿Por qué necesita estas dependencias?
4. ¿Hay alguna dependencia crítica?"""
        
        return self.ask(question, focus_component=component)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso"""
        overview = self.shadow.get_system_overview() if hasattr(self.shadow, 'get_system_overview') else {}
        
        return {
            'gemini': {
                'model': self.model_name,
                'queries': self.stats['queries'],
                'errors': self.stats['errors'],
                'conversation_length': len(self.conversation_history)
            },
            'shadow': {
                'mode': self.shadow_mode,
                'overview': overview
            }
        }
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history = []
        print("[GeminiShadow] Historial limpiado")
    
    def interactive_mode(self):
        """
        Modo interactivo: hacer preguntas en un loop
        """
        print("\n" + "="*60)
        print("🤖 GEMINI SHADOW - MODO INTERACTIVO")
        print("="*60)
        print("\nPregunta sobre el sistema Aipha_0.0.1")
        print(f"Modo: {self.shadow_mode}")
        print("\nComandos especiales:")
        print("  'context'      - Ver contexto completo")
        print("  'architecture' - Explicar arquitectura")
        print("  'component X'  - Analizar componente X")
        print("  'search X'     - Buscar y explicar X")
        print("  'stats'        - Ver estadísticas")
        print("  'clear'        - Limpiar historial")
        print("  'help'         - Mostrar ayuda")
        print("  'exit'         - Salir")
        print("\n" + "="*60 + "\n")
        
        while True:
            try:
                question = input("🔍 Pregunta: ").strip()
                
                if not question:
                    continue
                
                # Comandos especiales
                if question.lower() == 'exit':
                    print("\n👋 ¡Hasta luego!")
                    break
                
                elif question.lower() == 'context':
                    print("\n📄 CONTEXTO:")
                    print(self.system_context[:1000] + "...\n")
                
                elif question.lower() == 'architecture':
                    print("\n🏗️  ARQUITECTURA:")
                    print(self.get_architecture_explanation())
                    print()
                
                elif question.lower().startswith('component '):
                    component = question.split(' ', 1)[1]
                    print(f"\n📦 ANÁLISIS DE '{component}':")
                    print(self.ask_about_component(component))
                    print()
                
                elif question.lower().startswith('search '):
                    keyword = question.split(' ', 1)[1]
                    print(f"\n🔎 BÚSQUEDA: '{keyword}'")
                    print(self.search_and_explain(keyword))
                    print()
                
                elif question.lower() == 'stats':
                    print("\n📊 ESTADÍSTICAS:")
                    stats = self.get_stats()
                    print(f"Consultas: {stats['gemini']['queries']}")
                    print(f"Errores: {stats['gemini']['errors']}")
                    print(f"Conversaciones: {stats['gemini']['conversation_length']}")
                    print()
                
                elif question.lower() == 'clear':
                    self.clear_history()
                
                elif question.lower() == 'help':
                    print("\n📖 AYUDA:")
                    print("- Haz preguntas naturales sobre el código")
                    print("- Usa comandos especiales para análisis específicos")
                    print("- El sistema mantiene contexto de la conversación")
                    print()
                
                else:
                    # Pregunta normal
                    print("\n💭 Consultando a Gemini...\n")
                    response = self.ask(question)
                    print(response)
                    print()
            
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")


# === FUNCIÓN DE USO FÁCIL ===

def ask_gemini_about_aipha(question: str, 
                           api_key: Optional[str] = None,
                           base_path: str = "../Aipha_0.0.1") -> str:
    """
    Interfaz simple para hacer preguntas sobre Aipha_0.0.1
    
    Args:
        question: Pregunta sobre el sistema
        api_key: API key de Gemini (opcional)
        base_path: Ruta al código
    
    Returns:
        Respuesta de Gemini con contexto de Shadow
    """
    try:
        gemini_shadow = GeminiShadow(api_key=api_key, base_path=base_path)
        return gemini_shadow.ask(question)
    except Exception as e:
        return f"Error: {str(e)}"


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    import sys
    
    # Verificar API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY no está configurada")
        print("\nConfigurar con:")
        print("  export GEMINI_API_KEY='tu_api_key'")
        print("\nO crear archivo .env:")
        print("  GEMINI_API_KEY=tu_api_key")
        sys.exit(1)
    
    try:
        # Inicializar GeminiShadow
        gemini_shadow = GeminiShadow()
        
        # Modo interactivo
        gemini_shadow.interactive_mode()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)