# aiphalab/memory_system.py
"""
Sistema de Memoria para AiphaLab (Shadow 2.0)
Versión mejorada compatible con arquitectura híbrida

PROPÓSITO:
- Registrar análisis de código en memoria persistente
- Mantener integridad con hashes encadenados
- Proveer interfaz simple para otras capas

COMPATIBLE CON:
- shadow_core.py (análisis especializado)
- shadow_hybrid.py (orquestador)
- shadow_query.py (consultas)
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import ast
import os


class AiphaLabMemory:
    """
    Sistema de memoria persistente con integridad garantizada.
    
    CARACTERÍSTICAS:
    - Almacenamiento JSON con hashes SHA-256
    - Cadena de integridad (blockchain-style)
    - Análisis AST de código Python
    - Registro de eventos del sistema
    """
    
    def __init__(self, memory_file: str = "aiphalab_memory.json"):
        """
        Inicializar sistema de memoria
        
        Args:
            memory_file: Ruta al archivo JSON de memoria
        """
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
        print(f"[Memory] Cargadas {len(self.memory)} entradas desde {memory_file}")
    
    def _load_memory(self) -> List[Dict[str, Any]]:
        """Cargar memoria desde archivo JSON"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Validar que sea una lista
                    if isinstance(data, list):
                        return data
                    print("[Memory] Advertencia: Formato incorrecto, iniciando nueva memoria")
                    return []
            return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Memory] Error cargando memoria: {e}")
            return []
    
    def _save_memory(self):
        """Guardar memoria a archivo JSON"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Memory] Error guardando memoria: {e}")
    
    def _calculate_hash(self, entry: Dict[str, Any]) -> str:
        """
        Calcular hash SHA-256 de una entrada
        
        Args:
            entry: Diccionario de entrada (sin 'entry_hash')
        
        Returns:
            Hash SHA-256 como string hexadecimal
        """
        # Remover entry_hash si existe para evitar recursión
        entry_for_hash = {k: v for k, v in entry.items() if k != 'entry_hash'}
        
        # Serializar de manera determinística
        content = json.dumps(entry_for_hash, sort_keys=True, ensure_ascii=False)
        
        # Calcular hash
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_previous_hash(self) -> str:
        """
        Obtener hash de la entrada anterior para mantener cadena
        
        Returns:
            Hash de la última entrada, o "" si no hay entradas
        """
        if not self.memory:
            return ""
        return self.memory[-1].get('entry_hash', '')
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verificar integridad de la cadena de memoria
        
        Returns:
            Diccionario con resultado de verificación
        """
        if not self.memory:
            return {
                'valid': True,
                'entries_checked': 0,
                'issues': []
            }
        
        issues = []
        previous_hash = ""
        
        for i, entry in enumerate(self.memory):
            # Verificar hash de entrada
            stored_hash = entry.get('entry_hash', '')
            calculated_hash = self._calculate_hash(entry)
            
            if stored_hash != calculated_hash:
                issues.append({
                    'index': i,
                    'type': 'hash_mismatch',
                    'entry_id': entry.get('entry_id'),
                    'message': f"Hash no coincide en entrada {i}"
                })
            
            # Verificar cadena
            expected_previous = entry.get('previous_entry_hash', '')
            if expected_previous != previous_hash:
                issues.append({
                    'index': i,
                    'type': 'chain_broken',
                    'entry_id': entry.get('entry_id'),
                    'message': f"Cadena rota en entrada {i}"
                })
            
            previous_hash = stored_hash
        
        return {
            'valid': len(issues) == 0,
            'entries_checked': len(self.memory),
            'issues': issues
        }
    
    def add_entry(self, 
                  action: str, 
                  component: str, 
                  details: Dict[str, Any], 
                  category: str = "SYSTEM_EVENT",
                  status: str = "success") -> str:
        """
        Agregar entrada a la memoria
        
        Args:
            action: Acción realizada (ej: "PYTHON_FILE_ANALYZED")
            component: Componente afectado (ej: "main.py")
            details: Detalles adicionales (dict)
            category: Categoría de la entrada
            status: Estado de la operación
        
        Returns:
            Hash de la entrada creada
        """
        entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version_id": "AiphaLab_1.0",
            "source_component": component,
            "entry_category": category,
            "action": action,
            "agent": "AiphaLab",
            "component": component,
            "status": status,
            "details": details,
            "data_payload": details,
            "previous_entry_hash": self._get_previous_hash(),
            "entry_hash": ""  # Se calculará después
        }
        
        # Calcular hash de la entrada
        entry["entry_hash"] = self._calculate_hash(entry)
        
        # Agregar a memoria
        self.memory.append(entry)
        
        # Guardar
        self._save_memory()
        
        return entry["entry_hash"]
    
    def analyze_codebase(self, repo_path: str):
        """
        Analizar un codebase completo y registrar en memoria
        
        Args:
            repo_path: Ruta al repositorio a analizar
        """
        repo_path = Path(repo_path)
        
        if not repo_path.exists():
            raise FileNotFoundError(f"Repositorio no encontrado: {repo_path}")
        
        print(f"[Memory] Analizando código en: {repo_path}")
        
        # Analizar archivos Python
        python_files = list(repo_path.glob("*.py"))
        
        for file_path in python_files:
            self._analyze_python_file(file_path)
        
        # Analizar archivos JSON
        json_files = list(repo_path.glob("*.json"))
        
        for file_path in json_files:
            self._analyze_json_file(file_path)
        
        # Registrar análisis completo
        self.add_entry(
            action="CODEBASE_ANALYSIS_COMPLETE",
            component="AiphaLab",
            details={
                "python_files_analyzed": len(python_files),
                "json_files_analyzed": len(json_files),
                "total_files": len(python_files) + len(json_files),
                "repository_path": str(repo_path)
            },
            category="CODE_ANALYSIS"
        )
        
        print(f"[Memory] Análisis completado: {len(python_files)} archivos Python, {len(json_files)} archivos JSON")
    
    def _analyze_python_file(self, file_path: Path):
        """
        Analizar un archivo Python y registrar en memoria
        
        Args:
            file_path: Ruta al archivo Python
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsear AST
            tree = ast.parse(content)
            
            # Extraer información
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Registrar en memoria
            self.add_entry(
                action="PYTHON_FILE_ANALYZED",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "classes": classes,
                    "functions": functions,
                    "imports": list(set(imports)),  # Únicos
                    "lines_of_code": len(content.splitlines()),
                    "file_size": len(content)
                },
                category="CODE_ANALYSIS"
            )
            
        except SyntaxError as e:
            self.add_entry(
                action="PYTHON_FILE_ANALYSIS_ERROR",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "error": str(e),
                    "error_type": "SyntaxError"
                },
                category="CODE_ANALYSIS",
                status="error"
            )
        except Exception as e:
            self.add_entry(
                action="PYTHON_FILE_ANALYSIS_ERROR",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                category="CODE_ANALYSIS",
                status="error"
            )
    
    def _analyze_json_file(self, file_path: Path):
        """
        Analizar un archivo JSON y registrar en memoria
        
        Args:
            file_path: Ruta al archivo JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            # Registrar en memoria
            self.add_entry(
                action="JSON_FILE_ANALYZED",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "content_keys": list(content.keys()) if isinstance(content, dict) else None,
                    "content_type": type(content).__name__,
                    "entries_count": len(content) if isinstance(content, (list, dict)) else None,
                    "file_size": os.path.getsize(file_path)
                },
                category="CODE_ANALYSIS"
            )
            
        except json.JSONDecodeError as e:
            self.add_entry(
                action="JSON_FILE_ANALYSIS_ERROR",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "error": str(e),
                    "error_type": "JSONDecodeError"
                },
                category="CODE_ANALYSIS",
                status="error"
            )
        except Exception as e:
            self.add_entry(
                action="JSON_FILE_ANALYSIS_ERROR",
                component=file_path.name,
                details={
                    "file_path": str(file_path),
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                category="CODE_ANALYSIS",
                status="error"
            )
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de la memoria
        
        Returns:
            Diccionario con estadísticas de memoria
        """
        if not self.memory:
            return {
                "total_entries": 0,
                "categories": {},
                "components": {},
                "status": {}
            }
        
        categories = {}
        components = {}
        statuses = {}
        
        for entry in self.memory:
            # Contar por categoría
            category = entry.get('entry_category', 'UNKNOWN')
            categories[category] = categories.get(category, 0) + 1
            
            # Contar por componente
            component = entry.get('component', 'UNKNOWN')
            components[component] = components.get(component, 0) + 1
            
            # Contar por status
            status = entry.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_entries": len(self.memory),
            "categories": categories,
            "components": components,
            "status": statuses,
            "first_entry": self.memory[0].get('timestamp') if self.memory else None,
            "last_entry": self.memory[-1].get('timestamp') if self.memory else None
        }
    
    def get_entries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Obtener todas las entradas de una categoría"""
        return [e for e in self.memory if e.get('entry_category') == category]
    
    def get_entries_by_component(self, component: str) -> List[Dict[str, Any]]:
        """Obtener todas las entradas de un componente"""
        return [e for e in self.memory if e.get('component') == component]
    
    def get_latest_entry(self, component: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtener la entrada más reciente
        
        Args:
            component: Filtrar por componente (opcional)
        
        Returns:
            Última entrada o None
        """
        if not self.memory:
            return None
        
        if component:
            entries = [e for e in self.memory if e.get('component') == component]
            return entries[-1] if entries else None
        
        return self.memory[-1]


# === FUNCIÓN DE USO FÁCIL ===

def analyze_aipha_codebase(repo_path: str = "../Aipha_0.0.1", 
                           memory_file: str = "aiphalab_memory.json") -> Dict[str, Any]:
    """
    Función simple para analizar el código de Aipha_0.0.1
    
    Args:
        repo_path: Ruta al repositorio
        memory_file: Archivo de memoria
    
    Returns:
        Resumen del análisis
    """
    memory = AiphaLabMemory(memory_file)
    memory.analyze_codebase(repo_path)
    
    summary = memory.get_memory_summary()
    
    print("\n=== ANÁLISIS COMPLETADO ===")
    print(f"Total de entradas: {summary['total_entries']}")
    print(f"Categorías: {summary['categories']}")
    print(f"Componentes: {summary['components']}")
    print(f"Estado: {summary['status']}")
    
    # Verificar integridad
    integrity = memory.verify_integrity()
    print(f"\n=== VERIFICACIÓN DE INTEGRIDAD ===")
    print(f"Válido: {integrity['valid']}")
    print(f"Entradas verificadas: {integrity['entries_checked']}")
    if integrity['issues']:
        print(f"Problemas encontrados: {len(integrity['issues'])}")
        for issue in integrity['issues']:
            print(f"  - {issue['message']}")
    
    return summary


if __name__ == "__main__":
    # Ejemplo de uso
    analyze_aipha_codebase()