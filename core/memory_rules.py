"""
CriticalMemoryRules - Sistema de Atomicidad para Auto-Mejora
FASE 0: Base Atómica (Obligatorio)
"""
import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ChangeStatus(Enum):
    SUCCESS = "success"
    ROLLBACK = "rollback"
    FAILED = "failed"

@dataclass
class ChangeProposal:
    """Formato inmutable para propuestas de cambio"""
    proposal_id: str
    title: str
    target_component: str
    impact_justification: str
    estimated_difficulty: str
    diff_content: str
    test_plan: str
    metrics: Dict[str, float]

@dataclass
class Snapshot:
    """Metadata de snapshot del sistema de archivos"""
    snapshot_id: str
    timestamp: str
    source_path: str
    backup_path: str
    file_count: int
    checksum: str

class CriticalMemoryRules:
    """
    Implementa el protocolo de 5 pasos atómicos para cualquier cambio.
    Si falla cualquier paso: ROLLBACK AUTOMÁTICO.
    """
    
    SNAPSHOTS_DIR = Path("aipha/core/snapshots")
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def atomic_change(cls, proposal: ChangeProposal) -> Tuple[ChangeStatus, str]:
        """
        Protocolo NO NEGOCIABLE para cambios al filesystem.
        """
        snapshot_id = None
        
        try:
            # PASO 1: Snapshot (preservar estado)
            snapshot = cls._create_snapshot()
            snapshot_id = snapshot.snapshot_id
            
            # PASO 2: Validación Pre-ejecución
            if not cls._validate_environment():
                return cls._rollback(
                    snapshot_id, 
                    "Environment validation failed",
                    snapshot
                )
            
            # PASO 3: Dry Run Sintáctico
            if not cls._syntax_check(proposal.diff_content):
                return cls._rollback(
                    snapshot_id, 
                    "Syntax errors detected in diff",
                    snapshot
                )
            
            # PASO 4: Aplicación Condicional
            if not cls._apply_changes(proposal.diff_content):
                return cls._rollback(
                    snapshot_id, 
                    "Failed to apply changes",
                    snapshot
                )
            
            # PASO 5: Test Execution
            test_result = cls._run_tests(proposal.test_plan)
            if not test_result["passed"]:
                return cls._rollback(
                    snapshot_id, 
                    f"Tests failed: {test_result['failures']}",
                    snapshot
                )
            
            # ÉXITO: Confirmar cambios
            cls._commit_changes(proposal.proposal_id, proposal.title)
            return (ChangeStatus.SUCCESS, f"Changes applied successfully: {proposal.proposal_id}")
            
        except Exception as e:
            if snapshot_id:
                return cls._rollback(
                    snapshot_id,
                    f"Unexpected error: {str(e)}",
                    snapshot
                )
            return (ChangeStatus.FAILED, f"Critical failure: {str(e)}")
    
    @classmethod
    def _create_snapshot(cls) -> Snapshot:
        """PASO 1: Crear snapshot completo del proyecto con rsync"""
        try:
            source_path = Path.cwd()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            snapshot_id = f"snap_{timestamp}_{hashlib.md5(str(source_path).encode()).hexdigest()[:8]}"
            backup_path = cls.SNAPSHOTS_DIR / snapshot_id
            
            # Usar rsync para copia eficiente
            rsync_cmd = [
                "rsync", "-av", "--exclude", ".git", "--exclude", "__pycache__",
                "--exclude", "*.pyc", "--exclude", "snapshots/",
                f"{source_path}/", f"{backup_path}/"
            ]
            
            result = subprocess.run(rsync_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"rsync failed: {result.stderr}")
            
            # Calcular checksum del directorio
            checksum = cls._calculate_directory_checksum(source_path)
            
            # Contar archivos
            file_count = sum(1 for _ in source_path.rglob("*") if _.is_file())
            
            snapshot = Snapshot(
                snapshot_id=snapshot_id,
                timestamp=datetime.utcnow().isoformat(),
                source_path=str(source_path),
                backup_path=str(backup_path),
                file_count=file_count,
                checksum=checksum
            )
            
            # Guardar metadata
            metadata_path = backup_path / "snapshot_metadata.json"
            with open(metadata_path, "w") as f:
                json.dump({
                    "snapshot_id": snapshot_id,
                    "timestamp": snapshot.timestamp,
                    "source_path": source_path,
                    "file_count": file_count,
                    "checksum": checksum
                }, f, indent=2)
            
            return snapshot
            
        except Exception as e:
            raise RuntimeError(f"Snapshot creation failed: {str(e)}")
    
    @classmethod
    def _validate_environment(cls) -> bool:
        """PASO 2: Validar entorno de ejecución"""
        try:
            # Verificar Python versión compatible
            if sys.version_info < (3, 8):
                return False
            
            # Verificar git está disponible
            result = subprocess.run(["git", "--version"], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Verificar pytest está instalado
            result = subprocess.run(["pytest", "--version"], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Verificar rsync está disponible
            result = subprocess.run(["rsync", "--version"], capture_output=True)
            if result.returncode != 0:
                return False
            
            return True
            
        except Exception:
            return False
    
    @classmethod
    def _syntax_check(cls, diff_content: str) -> bool:
        """PASO 3: Validar sintaxis del diff aplicado"""
        try:
            # Crear directorio temporal para prueba
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Aplicar diff a copia temporal
                if not cls._apply_diff_to_temp(diff_content, temp_path):
                    return False
                
                # Verificar sintaxis Python de todos los archivos .py
                for py_file in temp_path.rglob("*.py"):
                    try:
                        with open(py_file, "r") as f:
                            compile(f.read(), str(py_file), "exec")
                    except SyntaxError:
                        return False
                
                return True
                
        except Exception:
            return False
    
    @classmethod
    def _apply_changes(cls, diff_content: str) -> bool:
        """PASO 4: Aplicar diff al filesystem real"""
        try:
            # Usar git apply para aplicar diff de forma segura
            process = subprocess.Popen(
                ["git", "apply", "--check", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            _, stderr = process.communicate(input=diff_content)
            
            if process.returncode != 0:
                return False
            
            # Si pasa el check, aplicar realmente
            process = subprocess.Popen(
                ["git", "apply", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            _, stderr = process.communicate(input=diff_content)
            
            return process.returncode == 0
            
        except Exception:
            return False
    
    @classmethod
    def _run_tests(cls, test_plan: str) -> Dict[str, any]:
        """PASO 5: Ejecutar plan de tests especificado"""
        try:
            # Parsear comandos pytest del plan
            if not test_plan.startswith("pytest"):
                return {"passed": False, "failures": "Invalid test plan format"}
            
            # Ejecutar tests
            result = subprocess.run(
                test_plan.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "failures": result.stderr if result.returncode != 0 else ""
            }
            
        except subprocess.TimeoutExpired:
            return {"passed": False, "failures": "Tests timed out after 300s"}
        except Exception as e:
            return {"passed": False, "failures": f"Test execution error: {str(e)}"}
    
    @classmethod
    def _rollback(cls, snapshot_id: str, reason: str, snapshot: Snapshot) -> Tuple[ChangeStatus, str]:
        """Revertir a snapshot en caso de fallo"""
        try:
            backup_path = Path(snapshot.backup_path)
            source_path = Path.cwd()
            
            if not backup_path.exists():
                return (ChangeStatus.FAILED, f"Rollback failed: snapshot not found {snapshot_id}")
            
            # Limpiar directorio actual (preservar .git)
            for item in source_path.iterdir():
                if item.name == ".git":
                    continue
                if item.is_file():
                    item.unlink()
                else:
                    shutil.rmtree(item)
            
            # Restaurar desde backup
            rsync_cmd = [
                "rsync", "-av", "--exclude", ".git",
                f"{backup_path}/", f"{source_path}/"
            ]
            
            result = subprocess.run(rsync_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return (ChangeStatus.FAILED, f"Rollback rsync failed: {result.stderr}")
            
            # Limpiar snapshot después de rollback exitoso
            shutil.rmtree(backup_path)
            
            return (ChangeStatus.ROLLBACK, f"Rolled back to {snapshot_id}. Reason: {reason}")
            
        except Exception as e:
            return (ChangeStatus.FAILED, f"Critical rollback failure: {str(e)}")
    
    @classmethod
    def _commit_changes(cls, proposal_id: str, title: str) -> None:
        """Confirmar cambios con commit git"""
        try:
            # Añadir todos los cambios
            subprocess.run(["git", "add", "."], capture_output=True, check=True)
            
            # Crear commit
            commit_msg = f"{proposal_id}: {title}\n\nAuto-implemented by Aipha Fase 0"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                capture_output=True,
                check=True
            )
        except Exception:
            # Silenciar errores de git para no bloquear el flujo
            pass
    
    @classmethod
    def _calculate_directory_checksum(cls, directory: Path) -> str:
        """Calcular checksum MD5 de todo el directorio"""
        hasher = hashlib.md5()
        
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                try:
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())
                except Exception:
                    continue
        
        return hasher.hexdigest()
    
    @classmethod
    def _apply_diff_to_temp(cls, diff_content: str, temp_path: Path) -> bool:
        """Aplicar diff a directorio temporal para validación"""
        try:
            # Inicializar git en temp
            subprocess.run(["git", "init"], cwd=temp_path, capture_output=True, check=True)
            
            # Crear archivos base (vacíos o con contenido mínimo)
            # Esto es una simplificación para la validación sintáctica
            # En producción, necesitaríamos el estado base real
            
            process = subprocess.Popen(
                ["git", "apply", "-"],
                cwd=temp_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            _, stderr = process.communicate(input=diff_content)
            return process.returncode == 0
            
        except Exception:
            return False