# AiphaLab - Sistema de Análisis de Código con IA

![AiphaLab Logo](https://img.shields.io/badge/AiphaLab-3.1.0-blue?style=for-the-badge&logo=python&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=flat-square&logo=python)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange?style=flat-square&logo=google)
![Moonshot](https://img.shields.io/badge/Moonshot-Kimi-purple?style=flat-square&logo=openai)
![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)

> **AiphaLab** es un sistema avanzado de análisis de código que combina análisis estático inteligente con capacidades de IA generativa para proporcionar insights profundos sobre bases de código complejas. Ahora con soporte multi-LLM (Gemini y Moonshot AI).

## 🚀 Características Principales

### 🤖 Análisis Inteligente
- **Core**: Análisis AST profundo de código Python
- **Hybrid**: Sistema híbrido con MCPs profesionales
- **Memoria Persistente**: Cache inteligente con SQLite
- **Verificación de Integridad**: Hashes SHA-256 para integridad de datos
- **Multi-LLM Support**: Integración con Gemini y Moonshot AI (Kimi)
- **Consulta Dual**: Análisis simultáneo de Aipha_0.0.1 y Aipha_1.0

### 🔍 Búsqueda Avanzada
- **Búsqueda Híbrida**: Combina ripgrep (veloz) con análisis estructural
- **Consultas Naturales**: Procesamiento de lenguaje natural con Gemini/Moonshot
- **Filtros Avanzados**: Por componente, categoría, agente, estado, etiquetas

### 📊 Estadísticas y Reportes
- **Métricas de Complejidad**: Análisis ciclomático y estadísticas de código
- **Historial Git**: Evolución histórica del código
- **Reportes Markdown**: Documentación automática de análisis

### 🛠️ MCPs Integrados
- **Filesystem MCP**: Lectura robusta de archivos
- **Ripgrep MCP**: Búsqueda ultrarrápida de texto
- **Git MCP**: Análisis incremental de cambios
- **SQLite Cache MCP**: Cache inteligente persistente

### 🤖 Proveedores LLM
- **Google Gemini**: Modelos avanzados de IA generativa
- **Moonshot AI (Kimi)**: IA especializada en razonamiento
- **Configuración Flexible**: Cambia entre proveedores fácilmente

## 📦 Instalación

### Opción 1: Instalador Automático (Recomendado)

```bash
# Clona el repositorio
git clone https://github.com/vaseksindelaru/aipha_0.0.1.git
cd aipha_0.0.1

# Ejecuta el instalador
./install_aiphalab.sh
```

### Opción 2: Instalación Manual

```bash
# Instala dependencias (elige tu proveedor LLM)
pip install google-generativeai  # Para Gemini
# O
pip install openai              # Para Moonshot AI

# Configura API key (elige uno)
export GEMINI_API_KEY="tu_api_key_aqui"
# O
export MOONSHOT_API_KEY="tu_api_key_aqui"

# Haz ejecutable el CLI
chmod +x aiphalab/aiphalab_cli.py
```

## 🎯 Uso Rápido

### 1. Ejecutar CLI
```bash
cd aiphalab
python aiphalab_cli.py
```

### 2. Verás el logo ASCII y el menú

```
======================================================================
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
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
    ======================================================================

Selecciona una opción:

  1. ⚙️ Asistente de Configuración
  2. 📊 Analizar Codebase
  3. 🤖 Modo Interactivo (Gemini/Moonshot)
  4. 📁 Ver Resumen del Sistema
  5. 🔍 Buscar en Código
  6. 📊 Ver Estadísticas

  0. Salir
```

### 3. Configuración Inicial
```bash
→ Opción: 1
```
El asistente verifica automáticamente:
- ✅ Dependencias instaladas
- ✅ API key configurada
- ✅ Directorio de Aipha encontrado

### 4. Analizar Codebase
```bash
→ Opción: 2
```
- Analizando código...
- ✅ Análisis completado!
- 📦 Componentes analizados: 15
- 📝 Entradas en memoria: 63

### 5. Modo Interactivo Multi-LLM
```bash
→ Opción: 3
```
El asistente configura automáticamente el proveedor LLM seleccionado y permite consultas interactivas.

```
🤖 GEMINI/MOONSHOT HYBRID - MODO INTERACTIVO

🔍 Pregunta: ¿Cuál es la arquitectura de Aipha_0.0.1?

💭 Consultando a [Gemini/Moonshot]...
```

## 🏗️ Arquitectura

```
AiphaLab/
├── aiphalab_cli.py          # 🖥️  Interfaz CLI profesional
├── core.py                  # 🧠 Núcleo de análisis AST
├── hybrid.py                # 🔄 Orquestador híbrido MCPs
├── mcp_adapters.py          # 🔌 Adaptadores MCP profesionales
├── gemini_integration.py    # 🤖 Integración con Gemini AI
└── memory files             # 💾 Archivos de memoria persistente
```

### Componentes Clave

#### Core
- **Propósito**: Análisis especializado de código Python
- **Tecnología**: AST parsing, análisis estático
- **Características**: Extrae clases, funciones, imports, docstrings

#### Hybrid
- **Propósito**: Orquestador inteligente
- **Tecnología**: Combina Core con MCPs
- **Características**: Cache inteligente, análisis incremental

#### MCP Adapters
- **Filesystem MCP**: Lectura robusta de archivos
- **Ripgrep MCP**: Búsqueda ultrarrápida
- **Git MCP**: Análisis de cambios versionados
- **SQLite Cache MCP**: Cache persistente

## 📚 API de Uso Programático

```python
from hybrid import Hybrid

# Inicializar sistema
hybrid = Hybrid(base_path="./tu_proyecto")

# Analizar codebase
hybrid.analyze_codebase(force=True)

# Buscar en código
resultados = hybrid.search("query", search_type='hybrid')

# Obtener contexto para LLM
contexto = hybrid.get_context_for_llm()

# Ver resumen
resumen = hybrid.get_system_overview()
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Elige tu proveedor LLM
export GEMINI_API_KEY="tu_api_key"        # Para Gemini
# O
export MOONSHOT_API_KEY="tu_api_key"      # Para Moonshot AI

# Configuración adicional
export AIPHALAB_CACHE_DIR="./cache"
export AIPHALAB_MEMORY_FILE="./aiphalab_memory.json"
```

### Configuración Personalizada
```python
from aiphalab_cli import AiphaLabCLI

cli = AiphaLabCLI()
cli.config.update({
    'aipha_path': '/ruta/a/tu/proyecto',
    'cache_enabled': True,
    'analysis_depth': 'deep'
})
cli.save_config()
```

## 📊 Casos de Uso

### 🔍 Análisis de Código Legacy
- Entender bases de código complejas
- Documentar arquitectura automáticamente
- Identificar áreas de mejora

### 🚀 Desarrollo Ágil
- Monitoreo continuo de cambios
- Análisis incremental rápido
- Consultas inteligentes sobre el código

### 📈 Investigación y Desarrollo
- Análisis de patrones de código
- Métricas de calidad automáticamente
- Integración con IA para insights profundos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Google Gemini**: Por capacidades de IA generativa avanzadas
- **Moonshot AI (Kimi)**: Por IA especializada en razonamiento
- **Aipha Community**: Por inspiración y feedback
- **Python AST**: Por análisis estático poderoso

## 📞 Soporte

- 📧 Email: support@aiphalab.dev
- 💬 Discord: [AiphaLab Community](https://discord.gg/aiphalab)
- 📖 Docs: [Documentación Completa](https://docs.aiphalab.dev)

---

**⭐ Si te gusta AiphaLab, dale una estrella en GitHub!**

> *Construido con ❤️ para la comunidad de desarrolladores*