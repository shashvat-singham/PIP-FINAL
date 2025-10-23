#!/usr/bin/env python3
"""
Setup script for Stock Research Platform
Handles environment setup, dependency installation, and configuration
"""
import os
import sys
import subprocess
import platform
from pathlib import Path
import argparse

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")

def check_python_version():
    """Check if Python version is 3.11 or higher"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_colored("❌ Error: Python 3.11 or higher is required", Colors.FAIL)
        print_colored("Please install Python 3.11+ from https://www.python.org/downloads/", Colors.WARNING)
        return False
    
    print_colored("✅ Python version is compatible", Colors.OKGREEN)
    return True

def check_node_installed():
    """Check if Node.js is installed"""
    print_header("Checking Node.js Installation")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Node.js version: {version}")
        print_colored("✅ Node.js is installed", Colors.OKGREEN)
        return True
    except FileNotFoundError:
        print_colored("⚠️  Node.js not found (required for React frontend)", Colors.WARNING)
        print_colored("Install from: https://nodejs.org/", Colors.WARNING)
        return False

def create_env_file():
    """Create .env file from template"""
    print_header("Setting Up Environment Variables")
    
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env'
    env_template = root_dir / '.env.template'
    
    if env_file.exists():
        print_colored("✅ .env file already exists", Colors.OKGREEN)
        
        # Check if API key is configured
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
                print_colored("⚠️  GEMINI_API_KEY not configured yet", Colors.WARNING)
                print_colored("Please edit .env and add your actual API key", Colors.WARNING)
        return True
    
    if not env_template.exists():
        print_colored("⚠️  .env.template not found, creating default .env", Colors.WARNING)
        with open(env_file, 'w') as f:
            f.write("# Google Gemini API Configuration\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n\n")
            f.write("# Application Configuration\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("ENVIRONMENT=development\n\n")
            f.write("# CORS Configuration\n")
            f.write("CORS_ORIGINS=http://localhost:3000\n\n")
            f.write("# Agent Configuration\n")
            f.write("MAX_ITERATIONS=3\n")
            f.write("AGENT_TIMEOUT=300\n")
    else:
        # Copy template to .env
        with open(env_template, 'r') as src:
            with open(env_file, 'w') as dst:
                dst.write(src.read())
    
    print_colored(f"✅ Created .env file at {env_file}", Colors.OKGREEN)
    print_colored("\n⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY", Colors.WARNING)
    return True

def install_backend_dependencies(force=False):
    """Install Python dependencies"""
    print_header("Installing Backend Dependencies")
    
    backend_dir = Path(__file__).parent.parent
    requirements_file = backend_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print_colored("❌ requirements.txt not found", Colors.FAIL)
        return False
    
    # Check if already installed (unless force)
    if not force:
        try:
            import fastapi
            import uvicorn
            import structlog
            print_colored("✅ Backend dependencies already installed (use --force to reinstall)", Colors.OKGREEN)
            return True
        except ImportError:
            pass
    
    print_colored("Installing Python packages...", Colors.OKCYAN)
    print_colored("This may take a few minutes...", Colors.OKCYAN)
    
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            check=True
        )
        print_colored("✅ Backend dependencies installed successfully", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error installing dependencies: {e}", Colors.FAIL)
        return False

def install_frontend_dependencies(force=False):
    """Install Node.js dependencies for frontend"""
    print_header("Installing Frontend Dependencies")
    
    frontend_dir = Path(__file__).parent.parent.parent / 'frontend' / 'stock-research-ui'
    
    if not frontend_dir.exists():
        print_colored("⚠️  Frontend directory not found, skipping", Colors.WARNING)
        return False
    
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        print_colored("⚠️  package.json not found, skipping", Colors.WARNING)
        return False
    
    node_modules = frontend_dir / 'node_modules'
    if node_modules.exists() and not force:
        print_colored("✅ Frontend dependencies already installed (use --force to reinstall)", Colors.OKGREEN)
        return True
    
    print_colored("Installing Node.js packages...", Colors.OKCYAN)
    print_colored("This may take a few minutes...", Colors.OKCYAN)
    
    try:
        # Use npm or yarn based on availability
        if platform.system() == 'Windows':
            npm_cmd = 'npm.cmd'
        else:
            npm_cmd = 'npm'
        
        subprocess.run(
            [npm_cmd, 'install', '--legacy-peer-deps'],
            cwd=frontend_dir,
            check=True
        )
        print_colored("✅ Frontend dependencies installed successfully", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Error installing frontend dependencies: {e}", Colors.FAIL)
        return False
    except FileNotFoundError:
        print_colored("⚠️  npm not found, skipping frontend setup", Colors.WARNING)
        print_colored("Install Node.js from: https://nodejs.org/", Colors.WARNING)
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    root_dir = Path(__file__).parent.parent.parent
    directories = [
        root_dir / 'data',
        root_dir / 'data' / 'chroma_db',
        root_dir / 'logs',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print_colored(f"✅ Created {directory.relative_to(root_dir)}", Colors.OKGREEN)
    
    return True

def verify_installation():
    """Verify that everything is installed correctly"""
    print_header("Verifying Installation")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import structlog
        from backend.tools.yahoo_finance_tool import YahooFinanceTool
        print_colored("✅ Backend packages verified", Colors.OKGREEN)
    except ImportError as e:
        print_colored(f"❌ Backend verification failed: {e}", Colors.FAIL)
        return False
    
    # Check .env file
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env'
    if not env_file.exists():
        print_colored("❌ .env file not found", Colors.FAIL)
        return False
    
    print_colored("✅ Installation verified successfully", Colors.OKGREEN)
    return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("Setup Complete!")
    
    print_colored("Next steps:", Colors.BOLD)
    
    print("\n1. Configure your API key:")
    print_colored("   Edit .env file and set:", Colors.OKCYAN)
    print("   GEMINI_API_KEY=your_actual_api_key")
    
    print("\n2. Start the application:")
    print_colored("   python scripts/start.py", Colors.OKGREEN)
    
    print("\n3. Access the application:")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Frontend UI: http://localhost:3000")
    
    print("\n4. Run tests:")
    print_colored("   pytest", Colors.OKCYAN)
    
    print("\n" + "=" * 60)
    print_colored("\n✨ You're all set! Run 'python scripts/start.py' to begin.", Colors.OKGREEN)
    print("=" * 60 + "\n")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='Setup Stock Research Platform')
    parser.add_argument('--force', action='store_true', help='Force reinstall all dependencies')
    parser.add_argument('--backend-only', action='store_true', help='Install only backend dependencies')
    parser.add_argument('--frontend-only', action='store_true', help='Install only frontend dependencies')
    parser.add_argument('--skip-verify', action='store_true', help='Skip installation verification')
    
    args = parser.parse_args()
    
    print_header("Stock Research Platform - Setup")
    
    success = True
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    node_available = check_node_installed()
    
    # Create environment file
    if not args.frontend_only:
        if not create_env_file():
            success = False
    
    # Create directories
    if not args.frontend_only:
        if not create_directories():
            success = False
    
    # Install dependencies
    if not args.frontend_only:
        if not install_backend_dependencies(force=args.force):
            success = False
    
    if not args.backend_only and node_available:
        if not install_frontend_dependencies(force=args.force):
            # Frontend is optional, don't fail
            pass
    
    # Verify installation
    if not args.skip_verify and not args.frontend_only:
        if not verify_installation():
            success = False
    
    # Print next steps
    if success:
        print_next_steps()
    else:
        print_colored("\n⚠️  Setup completed with some errors. Please check the output above.", Colors.WARNING)
        sys.exit(1)

if __name__ == '__main__':
    main()

