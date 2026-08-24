# Guía de instalación: Aseprite MCP

Servidor MCP que permite a asistentes de IA (Claude Code, Cursor, Devin, VS Code)
controlar Aseprite para crear pixel art y animaciones: **104 herramientas** de
dibujo, capas, animación, paletas, efectos, exportación y más.

---

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| **Aseprite** | Instalado o compilado — solo necesitas la ruta al ejecutable |
| **uv** | Gestor de paquetes de Python — instala Python y las dependencias automáticamente |
| **Un cliente MCP** | Claude Code, Cursor, Devin, VS Code, etc. |

> **No necesitas** instalar Python manualmente, ni crear entornos virtuales,
> ni correr `pip install -r requirements.txt`. `uv` hace todo eso solo en el
> primer arranque.

---

## Paso 1: Instalar uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS con Homebrew
brew install uv

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verifica:

```bash
uv --version
```

## Paso 2: Localizar el ejecutable de Aseprite

El servidor lanza Aseprite en modo batch (sin abrir la interfaz), así que solo
necesitas la ruta al **binario**, no a la aplicación:

| Caso | Ruta típica |
|------|-------------|
| macOS (aseprite.org) | `/Applications/Aseprite.app/Contents/MacOS/aseprite` |
| macOS (Steam) | `~/Library/Application Support/Steam/steamapps/common/Aseprite/Aseprite.app/Contents/MacOS/aseprite` |
| macOS (compilado desde fuente) | `<repo-aseprite>/build/bin/Aseprite.app/Contents/MacOS/aseprite` |
| Windows (Steam) | `C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe` |
| Linux (Steam) | `~/.steam/steam/steamapps/common/Aseprite/aseprite` |

Verifica que funciona:

```bash
"<ruta-al-binario>" --version
# Debe responder algo como: Aseprite 1.3.x
```

## Paso 3: Clonar este repo

```bash
git clone https://github.com/alejandrocastellanos/aseprite-mcp.git
cd aseprite-mcp
```

## Paso 4: Configurar tu cliente

Cada cliente lee su propio archivo de configuración. Crea el que corresponda:

### Claude Code

Archivo: `.mcp.json` en la raíz del repo (ya incluido en este repositorio):

```json
{
  "mcpServers": {
    "aseprite": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "-m", "aseprite_mcp"],
      "env": {}
    }
  }
}
```

Claude Code lanza el servidor con la raíz del proyecto como directorio de
trabajo, por eso no necesita `--directory`. La ruta de Aseprite la toma del
`.env` (ver Paso 5).

### Cursor

Archivo: `.cursor/mcp.json` en la raíz del repo:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "<ruta-completa-a-uv>",
      "args": ["--directory", "<ruta-completa-al-repo>", "run", "-m", "aseprite_mcp"],
      "env": {
        "ASEPRITE_PATH": "<ruta-al-binario-de-aseprite>"
      }
    }
  }
}
```

### Devin

Archivo: `.devin/mcp_config.json` en la raíz del repo
(o `~/.config/devin/mcp_config.json` para tenerlo en todos los proyectos):

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "<ruta-completa-a-uv>",
      "args": ["--directory", "<ruta-completa-al-repo>", "run", "-m", "aseprite_mcp"],
      "env": {
        "ASEPRITE_PATH": "<ruta-al-binario-de-aseprite>"
      }
    }
  }
}
```

### VS Code

Archivo: `.vscode/mcp.json` en la raíz del repo, misma estructura `mcpServers`.

### Notas importantes sobre el JSON

- Usa la **ruta completa a `uv`** (encuéntrala con `which uv` / `where uv`),
  porque los IDE no siempre heredan el `PATH` de tu terminal.
- `--directory <repo>` le dice a `uv` dónde está el proyecto sin importar
  desde qué carpeta lo lance el IDE.
- `ASEPRITE_PATH` en el `env` es la opción recomendada; la alternativa es el
  `.env` del Paso 5.

## Paso 5 (alternativa): archivo .env

Si prefieres no poner la ruta de Aseprite en el JSON de cada cliente, crea un
archivo `.env` en la raíz del repo:

```bash
ASEPRITE_PATH=<ruta-al-binario-de-aseprite>
```

El servidor lo carga automáticamente al arrancar. (Este archivo está en
`.gitignore` — es local a tu máquina.)

## Paso 6: Reiniciar el IDE y aprobar

1. Cierra y vuelve a abrir el IDE en la carpeta del repo.
2. **Aprueba el servidor cuando lo pregunte** — Claude Code y Cursor piden
   confirmación la primera vez por seguridad. Este paso es obligatorio;
   sin la aprobación el servidor queda en "pending".
3. El primer arranque tarda unos segundos extra: `uv` está descargando
   Python 3.13 y las dependencias. Los siguientes arranques son inmediatos.

## Paso 7: Verificar que funciona

Pídele al asistente:

> "Crea un canvas de 32×32 llamado test.aseprite y dibuja un cuadrado rojo"

Si aparece el archivo `test.aseprite` con el cuadrado, todo está funcionando.

Verificación desde terminal (opcional):

```bash
cd <repo>
uv run -m aseprite_mcp   # arranca el servidor, Ctrl+C para salir
```

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `uv: command not found` en el IDE | Pon la ruta completa a `uv` en el JSON (`which uv`) |
| El servidor arranca pero las herramientas fallan | `ASEPRITE_PATH` mal configurado — verifica con `"<ruta>" --version` |
| Servidor en "Pending approval" (Claude Code) | Abre `claude` en la carpeta y aprueba, o usa `/mcp` dentro de la sesión |
| Cambios en la config no se reflejan | Reinicia el IDE — los servidores MCP se conectan al iniciar la sesión |
| El primer arranque es lento | Normal: `uv` está instalando Python y dependencias; solo pasa una vez |

## Resumen en 30 segundos

1. Instalar `uv`
2. Saber la ruta al ejecutable de Aseprite
3. Clonar el repo
4. Crear el JSON de config de tu cliente (`.mcp.json` / `.cursor/mcp.json` / `.devin/mcp_config.json`)
   con `uv --directory <repo> run -m aseprite_mcp` y `ASEPRITE_PATH`
5. Reiniciar el IDE y **aprobar** el servidor
6. Pedir "crea un canvas de 32×32" y disfrutar
