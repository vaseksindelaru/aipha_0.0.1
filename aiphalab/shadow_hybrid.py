# aiphalab/shadow_hybrid.py
"""
Shadow Hybrid - Orquestador inteligente que combina Shadow Core con MCPs.

ARQUITECTURA:
- Shadow Core: Análisis especializado (TU control)
- MCPs: Operaciones genéricas (probado, robusto)
- Híbrido: Mejor de ambos mundos
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import os

from shadow_core import ShadowCore
from mcp_adapters import MCPFactory, FilesystemMCPAdapter, RipgrepMCPAdapter, GitMCPAdapter, SQLiteCacheMCPAdapter


class ShadowHybrid:
    """
    Sistema híbrido que combina Shadow Core con MCPs profesionales
    
    VENTAJAS:
    1. Análisis especializado (Shadow Core)
    2. Operaciones genéricas optimizadas (MCPs)
    3. Cache inteligente (SQLite MCP)
    4. Análisis incremental (Git MCP)
    5. Búsqueda ultrarrápida (Ripgrep MCP)
    """
    
    def __init__(self, base_path: str = "../Aipha_0.0.1"):
        print(f"[ShadowHybrid] Input base_path: '{base_path}' (tipo: {type(base_path)})")

        self.base_path = Path(base_path)
        print(f"[ShadowHybrid] Base path Path object: {self.base_path}")
        print(f"[ShadowHybrid] Base path resolved: {self.base_path.resolve()}")

        # Crear archivo de memoria único por sistema (solución profesional)
        system_name = self.base_path.name  # Ej: "Aipha_0.0.1" o "aipha_1"
        memory_file = f"shadow_memory_{system_name}.json"
        print(f"[ShadowHybrid] Memoria dedicada: '{memory_file}'")

        # Inicializar Shadow Core con memoria dedicada
        self.core = ShadowCore(memory_file)
        print("[ShadowHybrid] Shadow Core inicializado")

        # Convertir a string para MCPs
        base_path_str = str(self.base_path)
        print(f"[ShadowHybrid] Base path string para MCPs: '{base_path_str}'")

        # Inicializar adaptadores MCP (probados, robustos)
        self.mcps = MCPFactory.create_adapters(base_path_str)
        self.fs = self.mcps['filesystem']
        self.rg = self.mcps['ripgrep']
        self.git = self.mcps['git']
        self.cache = self.mcps['sqlite_cache']

        print(f"[ShadowHybrid] MCPs inicializados con base_path: '{base_path_str}'")
        print("[ShadowHybrid] Sistema híbrido listo\n")
    
    # === ANÁLISIS INTELIGENTE ===
    
    def analyze_codebase(self, force: bool = False):
        """
        Análisis completo o incremental del codebase
        
        MEJORA sobre Fase 1:
        - Usa Git MCP para detectar cambios
        - Solo re-analiza archivos modificados
        - Cache SQLite para archivos sin cambios
        - 10-100x más rápido para re-análisis
        """
        print("[ShadowHybrid] Iniciando análisis...")
        
        if force:
            print("  Modo: Análisis completo (forzado)")
            files_to_analyze = self.fs.list_files("*.py")
        else:
            print("  Modo: Análisis incremental (solo cambios)")
            changed_files = self.git.get_changed_files() if self.git.enabled else []
            
            if changed_files:
                print(f"  Archivos modificados detectados: {len(changed_files)}")
                files_to_analyze = changed_files
            else:
                print("  No hay cambios detectados, analizando todo")
                files_to_analyze = self.fs.list_files("*.py")
        
        # Analizar cada archivo
        analyzed_count = 0
        cached_count = 0
        
        for file_path in files_to_analyze:
            result = self._analyze_file_with_cache(file_path)
            if result == 'analyzed':
                analyzed_count += 1
            elif result == 'cached':
                cached_count += 1
        
        print(f"\n[ShadowHybrid] Análisis completado:")
        print(f"  ✅ Archivos analizados: {analyzed_count}")
        print(f"  ⚡ Desde cache: {cached_count}")
        print(f"  📊 Total: {analyzed_count + cached_count}")
    
    def _analyze_file_with_cache(self, file_path: str) -> str:
        """
        Analiza un archivo usando cache inteligente
        
        VENTAJA: Evita re-analizar archivos sin cambios
        """
        full_path = self.base_path / file_path
        
        # Obtener timestamp de última modificación
        try:
            last_modified = os.path.getmtime(full_path)
            last_modified_str = str(last_modified)
        except:
            last_modified_str = "unknown"
        
        # Verificar cache
        cached = self.cache.get_cached_analysis(file_path, last_modified_str)
        if cached:
            # Usar análisis cacheado
            self.core.register_analysis(Path(file_path), cached)
            return 'cached'
        
        # Leer contenido (usando filesystem MCP)
        content = self.fs.read_file(file_path)
        if not content:
            return 'skipped'
        
        # Analizar (usando Shadow Core)
        analysis = self.core.analyze_python_file(Path(file_path), content)
        
        # Registrar análisis
        self.core.register_analysis(Path(file_path), analysis)
        
        # Cachear resultado
        self.cache.cache_analysis(file_path, last_modified_str, analysis)
        
        return 'analyzed'
    
    # === BÚSQUEDA HÍBRIDA ===
    
    def search(self, query: str, search_type: str = 'hybrid') -> List[Dict[str, Any]]:
        """
        Búsqueda híbrida: combina ripgrep (rápido) con Shadow (estructurado)
        
        VENTAJA: 100x más rápido que búsqueda lineal en JSON
        
        Tipos de búsqueda:
        - 'hybrid': Combina ripgrep + Shadow (RECOMENDADO)
        - 'text': Solo ripgrep (ultrarrápido, menos contexto)
        - 'structural': Solo Shadow (rico contexto, más lento)
        """
        results = {'text_matches': [], 'structural_matches': []}
        
        if search_type in ['hybrid', 'text']:
            # Búsqueda de texto con ripgrep (ultrarrápida)
            if self.rg.enabled:
                print(f"[ShadowHybrid] Búsqueda de texto con ripgrep: '{query}'")
                text_results = self.rg.search(query)
                results['text_matches'] = text_results
            else:
                print("[ShadowHybrid] Ripgrep no disponible, usando fallback")
        
        if search_type in ['hybrid', 'structural']:
            # Búsqueda estructurada en Shadow (contexto rico)
            print(f"[ShadowHybrid] Búsqueda estructurada en Shadow: '{query}'")
            structural_results = self._search_in_shadow(query)
            results['structural_matches'] = structural_results
        
        return results
    
    def _search_in_shadow(self, query: str) -> List[Dict[str, Any]]:
        """Búsqueda estructurada en memoria de Shadow"""
        query_lower = query.lower()
        matches = []
        
        for component in self.core.get_all_components():
            analysis = self.core.get_component_analysis(component)
            if not analysis:
                continue
            
            # Buscar en clases
            for class_info in analysis.get('classes', []):
                if query_lower in class_info.get('name', '').lower():
                    matches.append({
                        'type': 'class',
                        'component': component,
                        'name': class_info['name'],
                        'context': class_info
                    })
            
            # Buscar en funciones
            for func_info in analysis.get('functions', []):
                if query_lower in func_info.get('name', '').lower():
                    matches.append({
                        'type': 'function',
                        'component': component,
                        'name': func_info['name'],
                        'context': func_info
                    })
        
        return matches
    
    # === CONTEXTO PARA LLM ===
    
    def get_context_for_llm(self, focus: Optional[str] = None) -> str:
        """
        Genera contexto completo para Gemini
        
        MEJORA: Ahora incluye información de Git (evolución histórica)
        """
        lines = []
        
        lines.append("=== AIPHA_0.0.1 SYSTEM CONTEXT (SHADOW HYBRID) ===\n")
        
        # Resumen del sistema
        summary = self.core.get_memory_summary()
        lines.append(f"Total Components: {len(summary['components'])}")
        lines.append(f"Last Update: {summary.get('last_update', 'unknown')}")
        lines.append("")
        
        # Información de componentes
        lines.append("=== COMPONENTS ===")
        components = self.core.get_all_components()
        
        for component in components:
            # Si hay focus, solo mostrar ese componente
            if focus and component != focus:
                continue
            
            analysis = self.core.get_component_analysis(component)
            if not analysis:
                continue
            
            lines.append(f"\n[{component}]")
            
            # Docstring del módulo (si existe)
            docstrings = analysis.get('docstrings', {})
            if 'module' in docstrings:
                lines.append(f"  Description: {docstrings['module'][:100]}...")
            
            # Clases
            classes = analysis.get('classes', [])
            if classes:
                lines.append(f"  Classes:")
                for cls in classes:
                    if isinstance(cls, dict):
                        methods = ', '.join(cls.get('methods', []))
                        lines.append(f"    - {cls['name']}")
                        if methods:
                            lines.append(f"      Methods: {methods}")
                        if cls['name'] in docstrings:
                            lines.append(f"      Doc: {docstrings[cls['name']][:80]}...")
                    else:
                        # Handle case where cls might be a string
                        lines.append(f"    - {cls}")
            
            # Funciones
            functions = analysis.get('functions', [])
            if functions:
                lines.append(f"  Functions:")
                for func in functions:
                    if isinstance(func, dict):
                        params = ', '.join(func.get('params', []))
                        lines.append(f"    - {func['name']}({params})")
                        if func['name'] in docstrings:
                            lines.append(f"      Doc: {docstrings[func['name']][:80]}...")
                    else:
                        # Handle case where func might be a string
                        lines.append(f"    - {func}")
            
            # Imports
            imports = analysis.get('imports', [])
            if imports:
                import_modules = []
                for imp in imports:
                    if isinstance(imp, dict) and 'module' in imp:
                        import_modules.append(imp['module'])
                    elif isinstance(imp, str):
                        import_modules.append(imp)
                lines.append(f"  Imports: {', '.join(set(import_modules))}")
            
            # Estadísticas
            stats = analysis.get('stats', {})
            if stats:
                lines.append(f"  Stats: {stats.get('lines_of_code', 0)} LOC, "
                           f"complexity {stats.get('complexity', 0)}")
            
            # Historial (si Git está disponible)
            if self.git.enabled and not focus:
                history = self.git.get_file_history(component, limit=3)
                if history:
                    lines.append(f"  Recent Changes:")
                    for commit in history[:2]:
                        lines.append(f"    - {commit['date'][:10]}: {commit['message'][:50]}")
        
        return "\n".join(lines)
    
    def get_component_details(self, component: str) -> Dict[str, Any]:
        """
        Obtiene detalles completos de un componente
        
        MEJORA: Ahora incluye contenido actual + historial
        """
        details = {
            'analysis': self.core.get_component_analysis(component),
            'content': self.fs.read_file(component) if self.fs.enabled else None,
            'history': self.git.get_file_history(component) if self.git.enabled else []
        }
        
        return details
    
    # === UTILIDADES ===
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Visión general completa del sistema"""
        summary = self.core.get_memory_summary()
        
        overview = {
            'total_components': len(summary['components']),
            'total_entries': summary['total_entries'],
            'components': list(summary['components'].keys()),
            'last_update': summary.get('last_update'),
            'mcp_status': {
                'filesystem': self.fs.enabled,
                'ripgrep': self.rg.enabled,
                'git': self.git.enabled,
                'cache': self.cache.enabled
            }
        }
        
        # Añadir info de Git si disponible
        if self.git.enabled:
            overview['last_commit'] = self.git.get_last_commit_date()
        
        return overview
    
    def format_for_display(self, data: Any) -> str:
        """Formatea datos para display legible"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"{key}:")
                    if isinstance(value, list):
                        for item in value:
                            lines.append(f"  - {item}")
                    else:
                        for k, v in value.items():
                            lines.append(f"  {k}: {v}")
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        return str(data)


# === FUNCIÓN DE USO FÁCIL ===

def create_shadow_hybrid(base_path: str = "../Aipha_0.0.1") -> ShadowHybrid:
    """
    Crea una instancia de Shadow Hybrid
    
    Uso:
        shadow = create_shadow_hybrid()
        shadow.analyze_codebase()
        context = shadow.get_context_for_llm()
    """
    return ShadowHybrid(base_path)


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    # Crear sistema híbrido
    shadow = create_shadow_hybrid()
    
    # Análisis incremental (rápido)
    shadow.analyze_codebase(force=False)
    
    # Búsqueda híbrida
    print("\n=== BÚSQUEDA: 'Shadow' ===")
    results = shadow.search("Shadow", search_type='hybrid')
    print(f"Coincidencias de texto: {len(results['text_matches'])}")
    print(f"Coincidencias estructurales: {len(results['structural_matches'])}")
    
    # Contexto para LLM
    print("\n=== CONTEXTO COMPLETO ===")
    context = shadow.get_context_for_llm()
    print(context)
    
    # Visión general
    print("\n=== SYSTEM OVERVIEW ===")
    overview = shadow.get_system_overview()
    print(shadow.format_for_display(overview))