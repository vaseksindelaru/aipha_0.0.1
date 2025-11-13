#!/usr/bin/env python3
"""
aipha_bridge.py - Puente entre AiphaLab CLI y Aipha_0.0.1
Ubicación: /home/vaclav/aipha_0.0.1/aiphalab/aipha_bridge.py

Propósito:
- CLI usa este puente para interactuar con Aipha_0.0.1
- Comparten la misma Capa 1 (ContextSentinel + KnowledgeManager)
- Procesa instrucciones del dev como si fueran de automejora

Versión: 1.0
Fecha: 2025-01-12
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Agregar aipha_0.0.1 al path para importar componentes
AIPHA_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(AIPHA_ROOT))

# Importar componentes de Aipha_0.0.1
try:
    # Importar directamente desde el archivo
    import importlib.util
    memory_rules_path = AIPHA_ROOT / "core" / "memory_rules.py"
    spec = importlib.util.spec_from_file_location("memory_rules", memory_rules_path)
    memory_rules_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memory_rules_module)

    CriticalMemoryRules = memory_rules_module.CriticalMemoryRules
    ChangeProposal = memory_rules_module.ChangeProposal
    ChangeStatus = memory_rules_module.ChangeStatus

    MEMORY_RULES_AVAILABLE = True
except Exception as e:
    MEMORY_RULES_AVAILABLE = False
    print(f"⚠️  Warning: memory_rules.py no disponible - {e}")

# Importar sistema Shadow del CLI
try:
    from hybrid import Hybrid
    SHADOW_AVAILABLE = True
except ImportError:
    SHADOW_AVAILABLE = False
    print("⚠️  Warning: hybrid.py no disponible")


class AiphaBridge:
    """
    Puente inteligente entre CLI y sistema autónomo.
    
    Flujo:
    1. Dev da instrucción al CLI
    2. CLI usa este bridge para procesarla
    3. Bridge traduce a ChangeProposal
    4. Ejecuta protocolo atómico
    5. Registra en memoria compartida
    """
    
    def __init__(self, aipha_root: str = None):
        """
        Inicializar el Bridge.
        
        Args:
            aipha_root: Ruta raíz del proyecto Aipha_0.0.1
        """
        self.aipha_root = Path(aipha_root or AIPHA_ROOT)
        self.memory_dir = self.aipha_root / "aipha_memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Archivos de memoria compartida
        self.action_history = self.memory_dir / "action_history.jsonl"
        self.global_state = self.memory_dir / "global_state.json"
        
        # Inicializar Shadow para análisis de código
        if SHADOW_AVAILABLE:
            self.shadow = Hybrid(str(self.aipha_root))
        else:
            self.shadow = None
            print("⚠️  Shadow no disponible - funcionalidad limitada")
        
        # Inicializar estado si no existe
        self._init_storage()
        
        print(f"[Bridge] ✅ Inicializado en {self.aipha_root}")
        print(f"[Bridge] Memoria: {self.memory_dir}")
        print(f"[Bridge] Memory Rules: {'✅ Disponible' if MEMORY_RULES_AVAILABLE else '❌ No disponible'}")
        print(f"[Bridge] Shadow: {'✅ Disponible' if SHADOW_AVAILABLE else '❌ No disponible'}")
    
    def _init_storage(self):
        """Inicializar archivos de memoria si no existen"""
        if not self.action_history.exists():
            self.action_history.touch()
            print(f"[Bridge] Creado: {self.action_history}")
        
        if not self.global_state.exists():
            initial_state = {
                "current_phase": "0",
                "phase_0_status": "IMPLEMENTED",  # Siempre IMPLEMENTED ya que memory_rules está disponible
                "last_update": datetime.utcnow().isoformat(),
                "components": {
                    "memory_rules": MEMORY_RULES_AVAILABLE,
                    "context_sentinel": False,
                    "change_proposer": False,
                    "proposal_evaluator": False,
                    "codecraft_sage": False
                }
            }
            with open(self.global_state, 'w') as f:
                json.dump(initial_state, f, indent=2)
            print(f"[Bridge] Creado: {self.global_state}")
    
    def add_action(self, agent: str, action: str, details: Dict[str, Any]):
        """
        Registrar acción en historial compartido.
        
        Args:
            agent: Nombre del agente ("CLI", "ChangeProposer", etc)
            action: Descripción de la acción
            details: Detalles adicionales
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "agent": agent,
            "action": action,
            "details": details
        }
        
        with open(self.action_history, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_history(self, agent: str = None, limit: int = None) -> list:
        """
        Leer historial de acciones (opcionalmente filtrado).
        
        Args:
            agent: Filtrar por agente específico
            limit: Limitar número de resultados
            
        Returns:
            Lista de acciones
        """
        if not self.action_history.exists():
            return []
        
        actions = []
        with open(self.action_history, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if agent is None or entry.get('agent') == agent:
                        actions.append(entry)
                except json.JSONDecodeError:
                    continue
        
        if limit:
            actions = actions[-limit:]
        
        return actions
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtener estado completo del sistema.
        
        Returns:
            Diccionario con estado actual
        """
        # Leer estado global
        with open(self.global_state, 'r') as f:
            global_state = json.load(f)
        
        # Analizar código con Shadow si está disponible
        codebase_stats = {}
        if self.shadow:
            try:
                self.shadow.analyze_codebase(force=False)
                codebase_stats = self.shadow.get_system_overview()
            except Exception as e:
                print(f"[Bridge] Error analizando codebase: {e}")
        
        # Historial reciente
        recent_actions = self.get_history(limit=10)
        
        # Verificar componentes críticos
        components_status = {
            "memory_rules": MEMORY_RULES_AVAILABLE,
            "context_sentinel": (self.aipha_root / "core/context_sentinel.py").exists(),
            "change_proposer": (self.aipha_root / "core/tools/change_proposer.py").exists(),
            "proposal_evaluator": (self.aipha_root / "core/tools/proposal_evaluator.py").exists(),
            "codecraft_sage": (self.aipha_root / "core/tools/codecraft_sage.py").exists()
        }

        # Actualizar estado global si memory_rules está disponible
        if MEMORY_RULES_AVAILABLE and global_state.get("phase_0_status") != "IMPLEMENTED":
            global_state["phase_0_status"] = "IMPLEMENTED"
            global_state["last_update"] = datetime.utcnow().isoformat()
            with open(self.global_state, 'w') as f:
                json.dump(global_state, f, indent=2)
        
        return {
            "current_phase": global_state.get("current_phase"),
            "phase_0_status": global_state.get("phase_0_status"),
            "components_status": components_status,
            "codebase_stats": codebase_stats,
            "recent_actions": recent_actions,
            "last_update": global_state.get("last_update")
        }
    
    def process_dev_instruction(self, instruction: str, llm_provider = None) -> Dict[str, Any]:
        """
        Procesar instrucción del desarrollador.
        
        Args:
            instruction: Texto libre del dev
            llm_provider: Instancia de LLM para generar propuesta
        
        Returns:
            Diccionario con resultado
        """
        # Registrar instrucción
        self.add_action("CLI", "dev_instruction_received", {"instruction": instruction})
        
        # Analizar contexto actual
        status = self.get_system_status()
        
        # Generar contexto para LLM si Shadow está disponible
        context = ""
        if self.shadow:
            try:
                context = self.shadow.get_context_for_llm()
            except Exception as e:
                print(f"[Bridge] Error obteniendo contexto: {e}")
                context = "Contexto no disponible"
        
        if llm_provider:
            # Construir prompt para LLM
            prompt = f"""
Contexto del sistema Aipha_0.0.1:
{context}

Estado actual:
- Fase: {status['current_phase']}
- Componentes: {status['components_status']}

Instrucción del desarrollador:
"{instruction}"

Genera una propuesta de cambio en formato ChangeProposal con:
- proposal_id: AIPHA-XXX (siguiente número secuencial)
- title: Título técnico conciso
- target_component: Archivo a modificar/crear
- impact_justification: Justificación con métricas
- estimated_difficulty: Low/Medium/High
- diff_content: Diff unificado (si aplica)
- test_plan: Comando pytest específico
- metrics: Diccionario con métricas

Responde SOLO con la propuesta en formato legible.
"""
            
            try:
                response = llm_provider.generate_content(prompt)
                
                # Registrar respuesta
                self.add_action("CLI", "llm_proposal_generated", {
                    "instruction": instruction,
                    "response_length": len(response)
                })
                
                return {
                    "status": "proposal_generated",
                    "proposal": response,
                    "system_status": status
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error generando propuesta: {str(e)}",
                    "system_status": status
                }
        else:
            return {
                "status": "no_llm_provider",
                "message": "Se requiere proveedor LLM para generar propuesta",
                "system_status": status
            }
    
    def apply_change(self, proposal_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplicar cambio usando protocolo atómico.
        
        Args:
            proposal_dict: Diccionario con campos de ChangeProposal
        
        Returns:
            Diccionario con resultado
        """
        if not MEMORY_RULES_AVAILABLE:
            return {
                "status": "error",
                "message": "memory_rules.py no disponible"
            }
        
        try:
            # Convertir dict a ChangeProposal
            proposal = ChangeProposal(**proposal_dict)
            
            # Registrar inicio
            self.add_action("Bridge", "atomic_change_started", {
                "proposal_id": proposal.proposal_id
            })
            
            # Ejecutar protocolo atómico
            status, message = CriticalMemoryRules.atomic_change(proposal)
            
            # Registrar resultado
            self.add_action("Bridge", "atomic_change_completed", {
                "proposal_id": proposal.proposal_id,
                "status": status.value,
                "message": message
            })
            
            # Actualizar estado global
            with open(self.global_state, 'r') as f:
                global_state = json.load(f)
            
            global_state["last_update"] = datetime.utcnow().isoformat()
            if status == ChangeStatus.SUCCESS:
                global_state["last_successful_change"] = proposal.proposal_id
            
            with open(self.global_state, 'w') as f:
                json.dump(global_state, f, indent=2)
            
            return {
                "status": status.value,
                "message": message,
                "proposal_id": proposal.proposal_id
            }
        
        except Exception as e:
            self.add_action("Bridge", "atomic_change_error", {
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"Error aplicando cambio: {str(e)}"
            }
    
    def get_next_task(self) -> Dict[str, Any]:
        """
        Determinar siguiente tarea según fase actual.
        
        Returns:
            Diccionario con recomendación
        """
        status = self.get_system_status()
        current_phase = status['current_phase']
        components = status['components_status']
        
        # Lógica de roadmap
        if current_phase == "0" and not components['context_sentinel']:
            return {
                "phase": "1",
                "task": "Implementar ContextSentinel",
                "file": "core/context_sentinel.py",
                "justification": "Fase 0 completa. Siguiente: memoria persistente.",
                "priority": "high"
            }
        elif components['context_sentinel'] and not components['change_proposer']:
            return {
                "phase": "2",
                "task": "Implementar ChangeProposer",
                "file": "core/tools/change_proposer.py",
                "justification": "Memoria lista. Siguiente: generador de propuestas.",
                "priority": "high"
            }
        elif components['change_proposer'] and not components['proposal_evaluator']:
            return {
                "phase": "2",
                "task": "Implementar ProposalEvaluator",
                "file": "core/tools/proposal_evaluator.py",
                "justification": "Proposer listo. Siguiente: evaluador de propuestas.",
                "priority": "high"
            }
        elif components['proposal_evaluator'] and not components['codecraft_sage']:
            return {
                "phase": "3",
                "task": "Implementar CodecraftSage",
                "file": "core/tools/codecraft_sage.py",
                "justification": "Evaluador listo. Siguiente: implementador de código.",
                "priority": "high"
            }
        else:
            return {
                "phase": "unknown",
                "task": "Revisar roadmap manualmente",
                "file": "N/A",
                "justification": "Estado no mapeado en lógica automática",
                "priority": "medium"
            }


# === FUNCIÓN DE PRUEBA ===

def test_bridge():
    """Función de prueba del bridge"""
    print("\n" + "="*70)
    print("PRUEBA DE AIPHA BRIDGE")
    print("="*70 + "\n")
    
    # Inicializar bridge
    bridge = AiphaBridge()
    
    # Obtener estado del sistema
    print("\n--- ESTADO DEL SISTEMA ---")
    status = bridge.get_system_status()
    print(f"Fase actual: {status['current_phase']}")
    print(f"Fase 0: {status['phase_0_status']}")
    print("\nComponentes:")
    for comp, exists in status['components_status'].items():
        icon = "✅" if exists else "❌"
        print(f"  {icon} {comp}")
    
    # Obtener siguiente tarea
    print("\n--- SIGUIENTE TAREA ---")
    next_task = bridge.get_next_task()
    print(f"Fase: {next_task['phase']}")
    print(f"Tarea: {next_task['task']}")
    print(f"Archivo: {next_task['file']}")
    print(f"Justificación: {next_task['justification']}")
    
    # Ver historial reciente
    print("\n--- HISTORIAL RECIENTE ---")
    history = bridge.get_history(limit=5)
    if history:
        for entry in history:
            print(f"[{entry['timestamp'][:19]}] {entry['agent']}: {entry['action']}")
    else:
        print("(No hay historial todavía)")
    
    print("\n" + "="*70)
    print("PRUEBA COMPLETADA")
    print("="*70 + "\n")


# === EJECUCIÓN DIRECTA ===

if __name__ == "__main__":
    test_bridge()

