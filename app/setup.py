#!/usr/bin/env python3
"""
Setup script for Local LM Document Assistant
Creates executable and installs CLI command
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform


def create_executable():
    """Create executable using PyInstaller"""
    print("Creating executable...")

    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Create spec file for PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['local_lm_assistant.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'chromadb',
        'sentence_transformers',
        'langchain',
        'requests',
        'sqlite3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='local_lm_assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    coerce_mixed_platform=True,
    icon=None,
)
"""

    with open("assistant.spec", "w") as f:
        f.write(spec_content.strip())

    # Build executable
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "assistant.spec"]
    subprocess.check_call(cmd)

    print("Executable created in dist/ directory")


def install_cli_command():
    """Install CLI command system-wide"""
    system = platform.system().lower()

    if system == "windows":
        install_windows()
    else:
        install_unix()


def install_windows():
    """Install on Windows"""
    print("Installing on Windows...")

    # Create batch file wrapper
    batch_content = """@echo off
python "%~dp0local_lm_assistant.py" %*
"""

    # Find a suitable installation directory
    install_dir = Path.home() / "AppData" / "Local" / "Programs" / "LocalLMAssistant"
    install_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    shutil.copy("local_lm_assistant.py", install_dir)

    # Create batch file
    batch_file = install_dir / "lm.bat"
    with open(batch_file, "w") as f:
        f.write(batch_content)

    # Add to PATH (requires admin rights, so we'll create a user script)
    user_scripts = (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
    )
    user_scripts.mkdir(parents=True, exist_ok=True)

    print(f"Installed to: {install_dir}")
    print(f"To use globally, add {install_dir} to your PATH")
    print("Or use the full path to lm.bat")


def install_unix():
    """Install on Unix-like systems (Linux/macOS)"""
    print("Installing on Unix-like system...")

    # Try to install to /usr/local/bin (system-wide)
    system_bin = Path("/usr/local/bin")
    user_bin = Path.home() / ".local" / "bin"

    # Choose installation directory
    if system_bin.exists() and os.access(system_bin, os.W_OK):
        install_dir = system_bin
        print("Installing system-wide to /usr/local/bin")
    else:
        install_dir = user_bin
        install_dir.mkdir(parents=True, exist_ok=True)
        print(f"Installing to user directory: {install_dir}")

    # Create executable script
    script_content = f"""#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from local_lm_assistant import main
    main()
"""

    # Copy main file
    shutil.copy("local_lm_assistant.py", install_dir)

    # Create CLI wrapper
    cli_file = install_dir / "lm"
    with open(cli_file, "w") as f:
        f.write(script_content)

    # Make executable
    os.chmod(cli_file, 0o755)

    print(f"Installed 'lm' command to: {install_dir}")

    if install_dir == user_bin:
        print("Make sure ~/.local/bin is in your PATH:")
        print("echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc")
        print("source ~/.bashrc")


def install_dependencies():
    """Install required Python dependencies"""
    print("Installing Python dependencies...")

    dependencies = [
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "langchain>=0.0.300",
        "pypdf>=3.0.0",
        "requests>=2.28.0",
        "numpy>=1.21.0",
        "faiss-cpu>=1.7.0",  # Optional but recommended for better performance
    ]

    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {dep}: {e}")
            print("You may need to install this manually")


def create_desktop_entry():
    """Create desktop entry for Linux"""
    if platform.system().lower() != "linux":
        return

    desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Local LM Assistant
Comment=AI Assistant for Document Q&A
Exec=lm --interactive
Icon=accessories-text-editor
Terminal=true
Categories=Office;Utility;
"""

    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    desktop_file = desktop_dir / "local-lm-assistant.desktop"
    with open(desktop_file, "w") as f:
        f.write(desktop_content)

    os.chmod(desktop_file, 0o644)
    print("Created desktop entry")


def setup_ollama():
    """Provide instructions for Ollama setup"""
    print("\n" + "=" * 50)
    print("OLLAMA SETUP REQUIRED")
    print("=" * 50)
    print("This assistant requires Ollama to run LLaMA models.")
    print("\n1. Install Ollama:")
    print("   Visit: https://ollama.ai")
    print("   Or run: curl -fsSL https://ollama.ai/install.sh | sh")
    print("\n2. Install a model (e.g., LLaMA 2):")
    print("   ollama pull llama2")
    print("   # or for a smaller model:")
    print("   ollama pull llama2:7b")
    print("\n3. Start Ollama service:")
    print("   ollama serve")
    print("\n4. Test the installation:")
    print("   lm --add-doc /path/to/document.txt")
    print("   lm --query 'What is this document about?'")
    print("=" * 50)


def main():
    print("Local LM Document Assistant Setup")
    print("=" * 40)

    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")

    try:
        # Install dependencies
        install_dependencies()

        # Install CLI command
        install_cli_command()

        # Create desktop entry (Linux only)
        create_desktop_entry()

        # Show Ollama setup instructions
        setup_ollama()

        print("\n✅ Installation complete!")
        print("\nQuick start:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Add documents: lm --add-dir /path/to/documents/")
        print("3. Ask questions: lm --query 'Your question here'")
        print("4. Interactive mode: lm --interactive")

    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
