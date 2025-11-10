# aiphalab/core.py
"""
Core - Sistema de análisis especializado para Aipha.
Enfocado en análisis AST y estructura, delega operaciones genéricas a MCPs.
"""

import json
import hashlib
import uuid
import ast
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

class Core:
    """
    Core de Shadow - Solo análisis especializado
    
    FILOSOFÍA:
    - Hace UNA cosa: análisis estructural de código
    - La hace BIEN: AST profundo, contexto rico
    - Delega el resto: lectura, búsqueda, cache a MCPs
    """
    
    def __init__(self, memory_file: str = "aiphalab_memory.json"):
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()
    
    def _load_memory(self) -> List[Dict[str, Any]]:
        """Cargar memoria desde archivo"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_memory(self):
        """Guardar memoria a archivo"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _calculate_hash(self, entry: Dict) -> str:
        """Calcular hash SHA-256 de una entrada"""
        entry_for_hash = {k: v for k, v in entry.items() if k != 'entry_hash'}
        content = json.dumps(entry_for_hash, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_previous_hash(self) -> str:
        """Obtener hash de la entrada anterior"""
        if not self.memory:
            return ""
        return self.memory[-1].get('entry_hash', '')
    
    def add_entry(self, action: str, component: str, details: Dict, 
                  category: str = "SYSTEM_EVENT") -> str:
        """
        Agregar entrada a la memoria
        
        MEJORA: Ahora con timestamps más precisos y metadata rica
        """
        entry = {
            "entry_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version_id": "AiphaLab_1.0",
            "source_component": component,
            "entry_category": category,
            "action": action,
            "agent": "Core",
            "component": component,
            "status": "success",
            "details": details,
            "data_payload": details,
            "previous_entry_hash": self._get_previous_hash(),
            "entry_hash": ""
        }
        
        entry["entry_hash"] = self._calculate_hash(entry)
        self.memory.append(entry)
        self._save_memory()
        return entry["entry_hash"]
    
    def analyze_python_file(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Análisis profundo de archivo Python
        
        MEJORA sobre Fase 1:
        - Extrae decoradores
        - Identifica docstrings
        - Analiza parámetros de funciones
        - Detecta tipos (type hints)
        - Extrae constantes
        """
        try:
            tree = ast.parse(content)
            
            analysis = {
                'classes': [],
                'functions': [],
                'imports': [],
                'constants': [],
                'decorators': [],
                'docstrings': {}
            }
            
            # Extraer docstring del módulo
            if (ast.get_docstring(tree)):
                analysis['docstrings']['module'] = ast.get_docstring(tree)
            
            for node in ast.walk(tree):
                # Clases
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'bases': [self._get_node_name(base) for base in node.bases],
                        'methods': [],
                        'decorators': [self._get_node_name(d) for d in node.decorator_list]
                    }
                    
                    # Docstring de clase
                    docstring = ast.get_docstring(node)
                    if docstring:
                        analysis['docstrings'][node.name] = docstring
                    
                    # Métodos de la clase
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append(item.name)
                    
                    analysis['classes'].append(class_info)
                
                # Funciones (nivel módulo)
                elif isinstance(node, ast.FunctionDef) and self._is_module_level(node, tree):
                    func_info = {
                        'name': node.name,
                        'params': [arg.arg for arg in node.args.args],
                        'decorators': [self._get_node_name(d) for d in node.decorator_list],
                        'returns': self._get_annotation(node.returns) if node.returns else None
                    }
                    
                    # Docstring de función
                    docstring = ast.get_docstring(node)
                    if docstring:
                        analysis['docstrings'][node.name] = docstring
                    
                    analysis['functions'].append(func_info)
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'type': 'import'
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': node.module,
                                'name': alias.name,
                                'alias': alias.asname,
                                'type': 'from'
                            })
                
                # Constantes (asignaciones nivel módulo)
                elif isinstance(node, ast.Assign) and self._is_module_level(node, tree):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            analysis['constants'].append({
                                'name': target.id,
                                'value': self._get_constant_value(node.value)
                            })
            
            # Estadísticas
            analysis['stats'] = {
                'lines_of_code': len(content.splitlines()),
                'file_size': len(content),
                'complexity': self._estimate_complexity(tree)
            }
            
            return analysis
        
        except Exception as e:
            return {
                'error': str(e),
                'file_path': str(file_path)
            }
    
    def _get_node_name(self, node) -> str:
        """Obtiene el nombre de un nodo AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        return str(type(node).__name__)
    
    def _get_annotation(self, node) -> Optional[str]:
        """Obtiene anotación de tipo"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return f"{self._get_node_name(node.value)}[...]"
        return None
    
    def _is_module_level(self, node, tree) -> bool:
        """Verifica si un nodo está a nivel módulo"""
        for item in tree.body:
            if item == node:
                return True
        return False
    
    def _get_constant_value(self, node) -> Any:
        """Extrae valor de una constante (si es simple)"""
        if isinstance(node, (ast.Str, ast.Num)):
            return node.n if isinstance(node, ast.Num) else node.s
        elif isinstance(node, ast.Constant):
            return node.value
        return "<complex>"
    
    def _estimate_complexity(self, tree) -> int:
        """Estimación simple de complejidad ciclomática"""
        complexity = 1  # Base
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def register_analysis(self, file_path: Path, analysis: Dict[str, Any]):
        """
        Registra análisis en memoria
        
        MEJORA: Ahora incluye metadata rica para ChangeEvaluator
        """
        self.add_entry(
            action="PYTHON_FILE_ANALYZED",
            component=file_path.name,
            details={
                'file_path': str(file_path),
                **analysis
            },
            category="CODE_ANALYSIS"
        )
    
    def get_component_analysis(self, component_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene el análisis más reciente de un componente"""
        for entry in reversed(self.memory):
            if (entry.get('component') == component_name and 
                entry.get('entry_category') == 'CODE_ANALYSIS'):
                return entry.get('details', {})
        return None
    
    def get_all_components(self) -> List[str]:
        """Lista todos los componentes analizados"""
        components = set()
        for entry in self.memory:
            if entry.get('entry_category') == 'CODE_ANALYSIS':
                components.add(entry.get('component'))
        return sorted(list(components))
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Resumen de la memoria"""
        if not self.memory:
            return {"total_entries": 0}
        
        categories = {}
        components = {}
        
        for entry in self.memory:
            category = entry.get('entry_category', 'UNKNOWN')
            component = entry.get('component', 'UNKNOWN')
            
            categories[category] = categories.get(category, 0) + 1
            components[component] = components.get(component, 0) + 1
        
        return {
            "total_entries": len(self.memory),
            "categories": categories,
            "components": components,
            "last_update": self.memory[-1].get('timestamp') if self.memory else None
        }