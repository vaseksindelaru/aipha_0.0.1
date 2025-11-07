# aiphalab/shadow_query.py
"""
Sistema de Consultas para Shadow
Interfaz para hacer consultas inteligentes sobre la memoria de AiphaLab

PROPÓSITO:
- Proveer interfaz simple para consultar memoria
- Generar contexto rico para LLMs
- Análisis y estadísticas del codebase

COMPATIBLE CON:
- memory_system.py (lectura de memoria)
- shadow_hybrid.py (orquestador)
- gemini_integration.py (LLM)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


class ShadowQuery:
    """
    Interfaz de consulta para Shadow.
    Permite hacer preguntas sobre el código analizado.
    
    CARACTERÍSTICAS:
    - Consultas por componente, clase, función
    - Búsqueda por keywords
    - Análisis de dependencias
    - Generación de contexto para LLMs
    """
    
    def __init__(self, memory_file: str = "aiphalab_memory.json"):
        """
        Inicializar sistema de consultas
        
        Args:
            memory_file: Ruta al archivo de memoria JSON
        """
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
        print(f"[ShadowQuery] Cargadas {len(self.memory)} entradas")
    
    def _load_memory(self) -> List[Dict[str, Any]]:
        """Cargar memoria desde archivo"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ShadowQuery] Error cargando memoria: {e}")
            return []
    
    def reload(self):
        """Recargar memoria desde disco (útil si se actualizó)"""
        self.memory = self._load_memory()
        print(f"[ShadowQuery] Memoria recargada: {len(self.memory)} entradas")
    
    # === CONSULTAS BÁSICAS ===
    
    def get_all_components(self) -> List[str]:
        """
        Lista todos los componentes (archivos) analizados
        
        Returns:
            Lista de nombres de componentes únicos
        """
        components = set()
        for entry in self.memory:
            if entry.get('entry_category') == 'CODE_ANALYSIS':
                component = entry.get('component')
                if component and component != 'AiphaLab':
                    components.add(component)
        return sorted(list(components))
    
    def get_component_details(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos del análisis de un componente
        
        Args:
            component_name: Nombre del archivo (ej: "main.py")
        
        Returns:
            Diccionario con detalles del componente o None
        """
        # Buscar la entrada más reciente de este componente
        for entry in reversed(self.memory):
            if (entry.get('component') == component_name and 
                entry.get('entry_category') == 'CODE_ANALYSIS' and
                entry.get('action') in ['PYTHON_FILE_ANALYZED', 'JSON_FILE_ANALYZED']):
                return entry.get('details', {})
        return None
    
    def get_all_classes(self) -> Dict[str, List[str]]:
        """
        Lista todas las clases encontradas, organizadas por archivo
        
        Returns:
            Diccionario {archivo: [clases]}
        """
        classes_by_file = {}
        for entry in self.memory:
            if entry.get('action') == 'PYTHON_FILE_ANALYZED':
                details = entry.get('details', {})
                component = entry.get('component')
                classes = details.get('classes', [])
                if classes:
                    classes_by_file[component] = classes
        return classes_by_file
    
    def get_all_functions(self) -> Dict[str, List[str]]:
        """
        Lista todas las funciones encontradas, organizadas por archivo
        
        Returns:
            Diccionario {archivo: [funciones]}
        """
        functions_by_file = {}
        for entry in self.memory:
            if entry.get('action') == 'PYTHON_FILE_ANALYZED':
                details = entry.get('details', {})
                component = entry.get('component')
                functions = details.get('functions', [])
                if functions:
                    functions_by_file[component] = functions
        return functions_by_file
    
    def get_dependencies(self, component_name: str) -> List[str]:
        """
        Obtiene las dependencias (imports) de un componente
        
        Args:
            component_name: Nombre del archivo
        
        Returns:
            Lista de imports/dependencias
        """
        details = self.get_component_details(component_name)
        if details:
            return details.get('imports', [])
        return []
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Busca componentes que contengan un keyword
        
        Args:
            keyword: Palabra clave a buscar (case-insensitive)
        
        Returns:
            Lista de entradas que coinciden con resultados estructurados
        """
        keyword_lower = keyword.lower()
        results = []
        
        for entry in self.memory:
            if entry.get('entry_category') != 'CODE_ANALYSIS':
                continue
            
            matches = []
            
            # Buscar en nombre de componente
            component = entry.get('component', '')
            if keyword_lower in component.lower():
                matches.append({
                    'type': 'component_name',
                    'value': component
                })
            
            # Buscar en detalles
            details = entry.get('details', {})
            if isinstance(details, dict):
                # Buscar en clases
                classes = details.get('classes', [])
                for cls in classes:
                    if keyword_lower in cls.lower():
                        matches.append({
                            'type': 'class',
                            'value': cls,
                            'component': component
                        })
                
                # Buscar en funciones
                functions = details.get('functions', [])
                for func in functions:
                    if keyword_lower in func.lower():
                        matches.append({
                            'type': 'function',
                            'value': func,
                            'component': component
                        })
                
                # Buscar en imports
                imports = details.get('imports', [])
                for imp in imports:
                    if keyword_lower in imp.lower():
                        matches.append({
                            'type': 'import',
                            'value': imp,
                            'component': component
                        })
            
            if matches:
                results.append({
                    'component': component,
                    'matches': matches,
                    'entry': entry
                })
        
        return results
    
    # === CONSULTAS AVANZADAS ===
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        Obtiene una visión general completa del sistema
        
        Returns:
            Diccionario con resumen del sistema
        """
        components = self.get_all_components()
        classes_by_file = self.get_all_classes()
        functions_by_file = self.get_all_functions()
        
        total_classes = sum(len(c) for c in classes_by_file.values())
        total_functions = sum(len(f) for f in functions_by_file.values())
        
        # Estadísticas de código
        total_loc = 0
        total_size = 0
        for component in components:
            details = self.get_component_details(component)
            if details:
                total_loc += details.get('lines_of_code', 0)
                total_size += details.get('file_size', 0)
        
        return {
            "total_components": len(components),
            "components": components,
            "total_classes": total_classes,
            "classes_by_file": classes_by_file,
            "total_functions": total_functions,
            "functions_by_file": functions_by_file,
            "total_entries": len(self.memory),
            "total_lines_of_code": total_loc,
            "total_size_bytes": total_size
        }
    
    def get_component_relationships(self) -> Dict[str, Dict[str, Any]]:
        """
        Identifica relaciones entre componentes basadas en imports
        
        Returns:
            Diccionario {archivo: {imports: [...], imported_by: [...]}}
        """
        relationships = defaultdict(lambda: {'imports': [], 'imported_by': []})
        components = self.get_all_components()
        
        # Construir grafo de dependencias
        for component in components:
            if component.endswith('.py'):
                imports = self.get_dependencies(component)
                relationships[component]['imports'] = imports
                
                # Buscar qué componentes importan a este
                for other_component in components:
                    if other_component != component:
                        other_imports = self.get_dependencies(other_component)
                        # Verificar si algún import se relaciona con este componente
                        component_base = component.replace('.py', '')
                        if any(component_base in imp for imp in other_imports):
                            relationships[component]['imported_by'].append(other_component)
        
        return dict(relationships)
    
    def get_complexity_analysis(self) -> Dict[str, Any]:
        """
        Análisis de complejidad del codebase
        
        Returns:
            Estadísticas de complejidad
        """
        complexity_data = {
            'by_component': {},
            'total_loc': 0,
            'average_loc_per_file': 0,
            'largest_file': None,
            'most_classes': None,
            'most_functions': None
        }
        
        components = self.get_all_components()
        
        if not components:
            return complexity_data
        
        loc_values = []
        
        for component in components:
            details = self.get_component_details(component)
            if details:
                loc = details.get('lines_of_code', 0)
                classes = len(details.get('classes', []))
                functions = len(details.get('functions', []))
                
                complexity_data['by_component'][component] = {
                    'lines_of_code': loc,
                    'classes': classes,
                    'functions': functions,
                    'complexity_score': loc + (classes * 10) + (functions * 5)
                }
                
                loc_values.append(loc)
                complexity_data['total_loc'] += loc
        
        if loc_values:
            complexity_data['average_loc_per_file'] = sum(loc_values) / len(loc_values)
        
        # Encontrar extremos
        if complexity_data['by_component']:
            largest = max(complexity_data['by_component'].items(), 
                         key=lambda x: x[1]['lines_of_code'])
            complexity_data['largest_file'] = {
                'component': largest[0],
                'lines_of_code': largest[1]['lines_of_code']
            }
            
            most_classes = max(complexity_data['by_component'].items(), 
                              key=lambda x: x[1]['classes'])
            if most_classes[1]['classes'] > 0:
                complexity_data['most_classes'] = {
                    'component': most_classes[0],
                    'count': most_classes[1]['classes']
                }
            
            most_functions = max(complexity_data['by_component'].items(), 
                                key=lambda x: x[1]['functions'])
            if most_functions[1]['functions'] > 0:
                complexity_data['most_functions'] = {
                    'component': most_functions[0],
                    'count': most_functions[1]['functions']
                }
        
        return complexity_data
    
    def find_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """
        Encuentra información sobre una clase específica
        
        Args:
            class_name: Nombre de la clase
        
        Returns:
            Información sobre la clase o None
        """
        all_classes = self.get_all_classes()
        
        for component, classes in all_classes.items():
            if class_name in classes:
                details = self.get_component_details(component)
                return {
                    'class_name': class_name,
                    'component': component,
                    'component_details': details
                }
        
        return None
    
    def find_function(self, function_name: str) -> List[Dict[str, Any]]:
        """
        Encuentra todas las funciones con un nombre dado
        
        Args:
            function_name: Nombre de la función
        
        Returns:
            Lista de ocurrencias de la función
        """
        all_functions = self.get_all_functions()
        results = []
        
        for component, functions in all_functions.items():
            if function_name in functions:
                details = self.get_component_details(component)
                results.append({
                    'function_name': function_name,
                    'component': component,
                    'component_details': details
                })
        
        return results
    
    # === CONTEXTO PARA LLM ===
    
    def get_context_for_gemini(self, focus: Optional[str] = None) -> str:
        """
        Genera un contexto completo y legible para Gemini
        
        Args:
            focus: Componente específico en el que enfocarse (opcional)
        
        Returns:
            String con todo el contexto del sistema
        """
        context = []
        context.append("=== AIPHA_0.0.1 SYSTEM CONTEXT ===\n")
        
        # Visión general
        overview = self.get_system_overview()
        context.append(f"Total Components: {overview['total_components']}")
        context.append(f"Total Classes: {overview['total_classes']}")
        context.append(f"Total Functions: {overview['total_functions']}")
        context.append(f"Total Lines of Code: {overview['total_lines_of_code']}")
        context.append("")
        
        # Componentes
        context.append("=== COMPONENTS ===")
        components = overview['components'] if not focus else [focus]
        
        for component in components:
            details = self.get_component_details(component)
            if not details:
                continue
            
            context.append(f"\n[{component}]")
            context.append(f"  Path: {details.get('file_path', 'unknown')}")
            context.append(f"  Lines: {details.get('lines_of_code', 0)}")
            
            # Clases
            classes = details.get('classes', [])
            if classes:
                context.append(f"  Classes: {', '.join(classes)}")
            
            # Funciones
            functions = details.get('functions', [])
            if functions:
                context.append(f"  Functions: {', '.join(functions)}")
            
            # Imports
            imports = details.get('imports', [])
            if imports:
                context.append(f"  Imports: {', '.join(imports)}")
        
        # Relaciones (solo si no hay focus)
        if not focus:
            context.append("\n=== COMPONENT RELATIONSHIPS ===")
            relationships = self.get_component_relationships()
            for component, rels in relationships.items():
                if rels['imports'] or rels['imported_by']:
                    context.append(f"\n[{component}]")
                    if rels['imports']:
                        context.append(f"  Imports: {', '.join(rels['imports'])}")
                    if rels['imported_by']:
                        context.append(f"  Imported by: {', '.join(rels['imported_by'])}")
        
        return "\n".join(context)
    
    def format_for_llm(self, data: Any) -> str:
        """
        Formatea datos para que sean fáciles de leer por un LLM
        
        Args:
            data: Datos a formatear
        
        Returns:
            String formateado y legible
        """
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, list):
                    lines.append(f"{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                lines.append(f"  {k}: {v}")
                        else:
                            lines.append(f"  - {item}")
                elif isinstance(value, dict):
                    lines.append(f"{key}:")
                    for k, v in value.items():
                        if isinstance(v, (list, dict)):
                            lines.append(f"  {k}: [complex]")
                        else:
                            lines.append(f"  {k}: {v}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            return "\n".join(f"- {item}" for item in data)
        return str(data)


# === FUNCIÓN DE USO FÁCIL ===

def query_shadow(question_type: str = "overview", **kwargs) -> str:
    """
    Interfaz simple para hacer consultas a Shadow
    
    Args:
        question_type: Tipo de consulta
        **kwargs: Argumentos adicionales
    
    Returns:
        Respuesta formateada
    
    Tipos de consulta:
        - 'overview': Visión general del sistema
        - 'context': Contexto completo para LLM
        - 'component': Detalles de un componente
        - 'classes': Todas las clases
        - 'functions': Todas las funciones
        - 'search': Buscar por keyword
        - 'relationships': Relaciones entre componentes
        - 'complexity': Análisis de complejidad
    """
    shadow = ShadowQuery()
    
    if question_type == "overview":
        return shadow.format_for_llm(shadow.get_system_overview())
    
    elif question_type == "context":
        focus = kwargs.get('focus')
        return shadow.get_context_for_gemini(focus=focus)
    
    elif question_type == "component":
        component = kwargs.get('component')
        if not component:
            return "Error: Se requiere 'component' parameter"
        details = shadow.get_component_details(component)
        return shadow.format_for_llm(details) if details else f"Component '{component}' not found"
    
    elif question_type == "classes":
        return shadow.format_for_llm(shadow.get_all_classes())
    
    elif question_type == "functions":
        return shadow.format_for_llm(shadow.get_all_functions())
    
    elif question_type == "search":
        keyword = kwargs.get('keyword')
        if not keyword:
            return "Error: Se requiere 'keyword' parameter"
        results = shadow.search_by_keyword(keyword)
        return shadow.format_for_llm(results) if results else f"No results for '{keyword}'"
    
    elif question_type == "relationships":
        return shadow.format_for_llm(shadow.get_component_relationships())
    
    elif question_type == "complexity":
        return shadow.format_for_llm(shadow.get_complexity_analysis())
    
    else:
        return f"Unknown question type: {question_type}. Valid types: overview, context, component, classes, functions, search, relationships, complexity"


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    print("=== SHADOW QUERY - EJEMPLOS ===\n")
    
    # Ejemplo 1: Visión general
    print("1. SYSTEM OVERVIEW")
    print(query_shadow("overview"))
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 2: Contexto para Gemini
    print("2. CONTEXT FOR GEMINI")
    print(query_shadow("context"))
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 3: Búsqueda
    print("3. SEARCH: 'Shadow'")
    print(query_shadow("search", keyword="Shadow"))
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 4: Análisis de complejidad
    print("4. COMPLEXITY ANALYSIS")
    print(query_shadow("complexity"))
    print("\n" + "="*50 + "\n")
    
    # Ejemplo 5: Relaciones
    print("5. COMPONENT RELATIONSHIPS")
    print(query_shadow("relationships"))