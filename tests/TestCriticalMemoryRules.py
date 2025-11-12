"""
Tests para CriticalMemoryRules - Cobertura 100%
FASE 0: Test de atomicidad
"""
import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import json
import os

# Añadir root al path para importar
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.memory_rules import (
    CriticalMemoryRules,
    ChangeProposal,
    ChangeStatus,
    Snapshot
)

class TestCriticalMemoryRules:
    """Test suite para el protocolo atómico de 5 pasos"""

    @pytest.fixture
    def sample_proposal(self):
        """Propuesta de prueba válida"""
        return ChangeProposal(
            proposal_id="AIPHA-TEST-001",
            title="Test implementation",
            target_component="tests/test_sample.py",
            impact_justification="Test metric: 0% → 100% coverage",
            estimated_difficulty="Low",
            diff_content="""diff --git a/tests/test_sample.py b/tests/test_sample.py
new file mode 100644
index 0000000..e69de29
""",
            test_plan="pytest tests/test_sample.py -v",
            metrics={"complexity_change": 0.0, "coverage_change": 100.0}
        )

    @pytest.fixture
    def temp_git_repo(self):
        """Fixture con repo git temporal limpio"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Inicializar git
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", "test@aipha.com"], cwd=repo_path, check=True)

            # Crear estructura de directorios
            (repo_path / "aiphalab" / "core").mkdir(parents=True)
            (repo_path / "tests").mkdir(parents=True)

            # Crear archivo inicial
            initial_file = repo_path / "README.md"
            initial_file.write_text("# Test Repo")

            # Commit inicial
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

            yield repo_path

    def test_create_snapshot_success(self, temp_git_repo):
        """Test PASO 1: Creación exitosa de snapshot"""
        # Cambiar al repo temporal
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Crear algunos archivos
            (temp_git_repo / "aiphalab" / "core" / "test_file.py").write_text("print('test')")
            (temp_git_repo / "tests" / "test_dummy.py").write_text("def test(): pass")

            snapshot = CriticalMemoryRules._create_snapshot()

            assert snapshot.snapshot_id.startswith("snap_")
            assert snapshot.file_count >= 3  # README + 2 archivos creados
            assert Path(snapshot.backup_path).exists()
            assert (Path(snapshot.backup_path) / "snapshot_metadata.json").exists()

        finally:
            os.chdir(original_cwd)

    def test_validate_environment_success(self):
        """Test PASO 2: Validación de entorno exitosa"""
        # Asume que el entorno de test tiene todo instalado
        result = CriticalMemoryRules._validate_environment()
        assert result is True

    @patch("subprocess.run")
    def test_validate_environment_no_git(self, mock_run):
        """Test PASO 2: Fallo cuando git no está disponible"""
        mock_run.return_value.returncode = 1

        result = CriticalMemoryRules._validate_environment()
        assert result is False

    def test_syntax_check_valid_python(self):
        """Test PASO 3: Validación sintáctica correcta"""
        valid_diff = """diff --git a/test.py b/test.py
new file mode 100644
index 0000000..38f46ec
--- /dev/null
+++ b/test.py
@@ -0,0 +1,2 @@
+def valid_function():
+    return 42
"""
        result = CriticalMemoryRules._syntax_check(valid_diff)
        assert result is True

    def test_syntax_check_invalid_python(self):
        """Test PASO 3: Detección de error sintáctico"""
        invalid_diff = """diff --git a/test.py b/test.py
new file mode 100644
index 0000000..38f46ec
--- /dev/null
+++ b/test.py
@@ -0,0 +1,2 @@
+def invalid(:
+    return 42
"""
        result = CriticalMemoryRules._syntax_check(invalid_diff)
        assert result is False

    def test_atomic_change_full_success(self, temp_git_repo, sample_proposal):
        """Test INTEGRACIÓN: Camino completo de éxito"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Mock para evitar ejecución real de pytest
            with patch.object(CriticalMemoryRules, "_run_tests") as mock_tests:
                mock_tests.return_value = {
                    "passed": True,
                    "stdout": "All tests passed",
                    "stderr": "",
                    "failures": ""
                }

                status, message = CriticalMemoryRules.atomic_change(sample_proposal)

                assert status == ChangeStatus.SUCCESS
                assert "AIPHA-TEST-001" in message

                # Verificar que se creó commit
                result = subprocess.run(
                    ["git", "log", "--oneline", "-1"],
                    capture_output=True,
                    text=True,
                    cwd=temp_git_repo
                )
                assert "AIPHA-TEST-001" in result.stdout

        finally:
            os.chdir(original_cwd)

    def test_atomic_change_rollback_on_syntax_error(self, temp_git_repo, sample_proposal):
        """Test ROLLBACK: Fallo en PASO 3 (sintaxis)"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Crear archivo corrupto
            sample_proposal.diff_content = """diff --git a/corrupt.py b/corrupt.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/corrupt.py
@@ -0,0 +1 @@
+def bad(:
"""

            status, message = CriticalMemoryRules.atomic_change(sample_proposal)

            assert status == ChangeStatus.ROLLBACK
            assert "Syntax errors detected" in message

            # Verificar que no se aplicaron cambios
            assert not (temp_git_repo / "corrupt.py").exists()

        finally:
            os.chdir(original_cwd)

    def test_atomic_change_rollback_on_test_failure(self, temp_git_repo, sample_proposal):
        """Test ROLLBACK: Fallo en PASO 5 (tests)"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Mock tests fallando
            with patch.object(CriticalMemoryRules, "_run_tests") as mock_tests:
                mock_tests.return_value = {
                    "passed": False,
                    "stdout": "",
                    "stderr": "Test test_sample.py::test_failure FAILED",
                    "failures": "AssertionError: expected 42, got 0"
                }

                status, message = CriticalMemoryRules.atomic_change(sample_proposal)

                assert status == ChangeStatus.ROLLBACK
                assert "Tests failed" in message

                # Verificar rollback
                assert not (temp_git_repo / "tests" / "test_sample.py").exists()

        finally:
            os.chdir(original_cwd)

    def test_rollback_preserves_state(self, temp_git_repo):
        """Test ROLLBACK: Verificar preservación completa del estado"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Crear estado inicial conocido
            test_file = temp_git_repo / "critical_file.py"
            test_content = "CRITICAL_DATA = 'preserve_this'"
            test_file.write_text(test_content)

            # Crear snapshot
            snapshot = CriticalMemoryRules._create_snapshot()

            # Modificar archivo
            test_file.write_text("CORRUPTED_DATA = 'lost'")

            # Forzar rollback
            status, message = CriticalMemoryRules._rollback(
                snapshot.snapshot_id,
                "Test rollback",
                snapshot
            )

            # Verificar estado restaurado
            assert status == ChangeStatus.ROLLBACK
            assert test_file.read_text() == test_content

        finally:
            os.chdir(original_cwd)

    def test_calculate_directory_checksum(self, temp_git_repo):
        """Test utilidad: checksum de directorio"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            checksum1 = CriticalMemoryRules._calculate_directory_checksum(temp_git_repo)

            # Modificar archivo
            (temp_git_repo / "new_file.txt").write_text("test")

            checksum2 = CriticalMemoryRules._calculate_directory_checksum(temp_git_repo)

            assert checksum1 != checksum2
            assert len(checksum1) == 32  # MD5
            assert len(checksum2) == 32

        finally:
            os.chdir(original_cwd)

    def test_apply_changes_with_git_apply(self, temp_git_repo):
        """Test PASO 4: Aplicación de diff con git apply"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Crear diff válido
            diff = """diff --git a/applied_file.py b/applied_file.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/applied_file.py
@@ -0,0 +1 @@
+print("applied")
"""

            result = CriticalMemoryRules._apply_changes(diff)
            assert result is True

            # Verificar archivo creado
            applied_file = temp_git_repo / "applied_file.py"
            assert applied_file.exists()
            assert "print(\"applied\")" in applied_file.read_text()

        finally:
            os.chdir(original_cwd)

    def test_run_tests_mocked(self):
        """Test PASO 5: Ejecución de tests con mocking"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_plan = f"pytest {tmpdir} -v"

            # No hay tests, pero debería ejecutar sin error de timeout
            result = CriticalMemoryRules._run_tests(test_plan)

            # Si pytest no encuentra tests, returncode es 5 (módulo pytest)
            # Pero nuestra función debería manejarlo
            assert isinstance(result, dict)
            assert "passed" in result

    def test_commit_changes_integration(self, temp_git_repo):
        """Test integración con git commit"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            # Crear archivo para commit
            (temp_git_repo / "commit_test.py").write_text("# test")

            CriticalMemoryRules._commit_changes("AIPHA-COMMIT-001", "Test commit")

            # Verificar commit
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"],
                capture_output=True,
                text=True,
                cwd=temp_git_repo
            )

            assert "AIPHA-COMMIT-001" in result.stdout

        finally:
            os.chdir(original_cwd)

    def test_snapshot_cleanup_on_rollback(self, temp_git_repo):
        """Test: Snapshot eliminado después de rollback exitoso"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            snapshot = CriticalMemoryRules._create_snapshot()
            backup_path = Path(snapshot.backup_path)

            assert backup_path.exists()

            # Forzar rollback
            CriticalMemoryRules._rollback(
                snapshot.snapshot_id,
                "Test cleanup",
                snapshot
            )

            # Snapshot debería ser eliminado después de rollback
            assert not backup_path.exists()

        finally:
            os.chdir(original_cwd)

    def test_invalid_diff_format(self):
        """Test: Manejo de diff mal formateado"""
        invalid_diff = "esto no es un diff válido"
        result = CriticalMemoryRules._apply_changes(invalid_diff)
        assert result is False

    def test_empty_proposal_handling(self, temp_git_repo):
        """Test: Manejo de propuesta vacía o inválida"""
        original_cwd = Path.cwd()
        os.chdir(temp_git_repo)

        try:
            empty_proposal = ChangeProposal(
                proposal_id="",
                title="",
                target_component="",
                impact_justification="",
                estimated_difficulty="Low",
                diff_content="",
                test_plan="",
                metrics={}
            )

            status, message = CriticalMemoryRules.atomic_change(empty_proposal)

            # Debería fallar en PASO 3 (sintaxis) o PASO 4 (aplicación)
            assert status in [ChangeStatus.ROLLBACK, ChangeStatus.FAILED]

        finally:
            os.chdir(original_cwd)