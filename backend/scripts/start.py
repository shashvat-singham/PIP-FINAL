#!/usr/bin/env python3
"""
Start script for Stock Research Platform
Handles starting backend and frontend services
"""
import os
import sys
import subprocess
import platform
import time
import signal
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

def check_env_file():
    """Check if .env file exists and has GEMINI_API_KEY"""
    print_header("Checking Environment Configuration")
    
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env'
    
    if not env_file.exists():
        print_colored("❌ .env file not found!", Colors.FAIL)
        print_colored("Please run: python scripts/setup.py first", Colors.WARNING)
        return False
    
    # Check if GEMINI_API_KEY is set
    with open(env_file, 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY=your_gemini_api_key_here' in content:
            print_colored("⚠️  GEMINI_API_KEY not configured!", Colors.WARNING)
            print_colored("Please edit .env and add your actual API key", Colors.WARNING)
            return False
        elif 'GEMINI_API_KEY=' not in content:
            print_colored("⚠️  GEMINI_API_KEY not found in .env", Colors.WARNING)
            return False
    
    print_colored("✅ Environment file configured", Colors.OKGREEN)
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    print_header("Checking Dependencies")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import structlog
        print_colored("✅ Backend dependencies installed", Colors.OKGREEN)
    except ImportError as e:
        print_colored(f"❌ Missing Python dependencies: {e}", Colors.FAIL)
        print_colored("Run: python scripts/setup.py --install-deps", Colors.WARNING)
        return False
    
    return True

def start_backend(port=8000):
    """Start the backend server"""
    print_header("Starting Backend Server")
    
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print_colored(f"Starting FastAPI server on port {port}...", Colors.OKCYAN)
    print_colored(f"API will be available at: http://localhost:{port}", Colors.OKBLUE)
    print_colored(f"API Docs at: http://localhost:{port}/docs", Colors.OKBLUE)
    
    # Set PYTHONPATH to include backend directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir.parent)
    
    try:
        # Start uvicorn
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', str(port),
            '--reload'
        ]
        
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=backend_dir
        )
        
        print_colored(f"✅ Backend server started (PID: {process.pid})", Colors.OKGREEN)
        return process
        
    except Exception as e:
        print_colored(f"❌ Failed to start backend: {e}", Colors.FAIL)
        return None

def start_frontend(port=3000):
    """Start the frontend development server"""
    print_header("Starting Frontend Server")
    
    frontend_dir = Path(__file__).parent.parent.parent / 'frontend' / 'stock-research-ui'
    
    if not frontend_dir.exists():
        print_colored("⚠️  Frontend directory not found, skipping", Colors.WARNING)
        return None
    
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        print_colored("⚠️  package.json not found, skipping", Colors.WARNING)
        return None
    
    # Check if node_modules exists
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        print_colored("Installing frontend dependencies...", Colors.OKCYAN)
        try:
            npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
            subprocess.run([npm_cmd, 'install', '--legacy-peer-deps'], cwd=frontend_dir, check=True)
        except Exception as e:
            print_colored(f"❌ Failed to install frontend dependencies: {e}", Colors.FAIL)
            return None
    
    print_colored(f"Starting React development server on port {port}...", Colors.OKCYAN)
    print_colored(f"Frontend will be available at: http://localhost:{port}", Colors.OKBLUE)
    
    try:
        npm_cmd = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
        
        # Set PORT environment variable
        env = os.environ.copy()
        env['PORT'] = str(port)
        env['BROWSER'] = 'none'  # Don't auto-open browser
        
        process = subprocess.Popen(
            [npm_cmd, 'start'],
            cwd=frontend_dir,
            env=env
        )
        
        print_colored(f"✅ Frontend server started (PID: {process.pid})", Colors.OKGREEN)
        return process
        
    except Exception as e:
        print_colored(f"❌ Failed to start frontend: {e}", Colors.FAIL)
        return None

def wait_for_backend(port=8000, timeout=30):
    """Wait for backend to be ready"""
    import time
    import socket
    
    print_colored("Waiting for backend to be ready...", Colors.OKCYAN)
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print_colored("✅ Backend is ready!", Colors.OKGREEN)
                return True
        except:
            pass
        time.sleep(1)
    
    print_colored("⚠️  Backend took longer than expected to start", Colors.WARNING)
    return False

def print_access_info(backend_port=8000, frontend_port=3000, frontend_started=False):
    """Print access information"""
    print_header("Application Started Successfully!")
    
    print_colored("Access the application:", Colors.BOLD)
    print(f"\n  📊 Backend API:       http://localhost:{backend_port}")
    print(f"  📖 API Documentation: http://localhost:{backend_port}/docs")
    print(f"  ❤️  Health Check:      http://localhost:{backend_port}/health")
    
    if frontend_started:
        print(f"  🎨 Frontend UI:       http://localhost:{frontend_port}")
    
    print("\n" + "=" * 60)
    print_colored("\nPress Ctrl+C to stop all services", Colors.WARNING)
    print("=" * 60 + "\n")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Start Stock Research Platform')
    parser.add_argument('--backend-only', action='store_true', help='Start only backend')
    parser.add_argument('--frontend-only', action='store_true', help='Start only frontend')
    parser.add_argument('--backend-port', type=int, default=8000, help='Backend port (default: 8000)')
    parser.add_argument('--frontend-port', type=int, default=3000, help='Frontend port (default: 3000)')
    parser.add_argument('--no-check', action='store_true', help='Skip dependency checks')
    
    args = parser.parse_args()
    
    print_header("Stock Research Platform - Startup")
    
    processes = []
    
    try:
        # Check environment and dependencies
        if not args.no_check:
            if not check_env_file():
                print_colored("\n❌ Setup incomplete. Please run: python scripts/setup.py", Colors.FAIL)
                sys.exit(1)
            
            if not check_dependencies():
                print_colored("\n❌ Dependencies not installed. Please run: python scripts/setup.py", Colors.FAIL)
                sys.exit(1)
        
        # Start backend
        if not args.frontend_only:
            backend_process = start_backend(args.backend_port)
            if backend_process:
                processes.append(backend_process)
                wait_for_backend(args.backend_port)
            else:
                print_colored("❌ Failed to start backend", Colors.FAIL)
                sys.exit(1)
        
        # Start frontend
        frontend_started = False
        if not args.backend_only:
            frontend_process = start_frontend(args.frontend_port)
            if frontend_process:
                processes.append(frontend_process)
                frontend_started = True
                time.sleep(3)  # Give frontend time to start
        
        # Print access information
        print_access_info(args.backend_port, args.frontend_port, frontend_started)
        
        # Keep running until Ctrl+C
        while True:
            time.sleep(1)
            # Check if processes are still running
            for proc in processes:
                if proc.poll() is not None:
                    print_colored(f"\n⚠️  Process {proc.pid} exited unexpectedly", Colors.WARNING)
                    raise KeyboardInterrupt
    
    except KeyboardInterrupt:
        print_colored("\n\nShutting down services...", Colors.WARNING)
        for proc in processes:
            try:
                if platform.system() == 'Windows':
                    proc.terminate()
                else:
                    proc.send_signal(signal.SIGTERM)
                proc.wait(timeout=5)
            except:
                proc.kill()
        print_colored("✅ All services stopped", Colors.OKGREEN)
    
    except Exception as e:
        print_colored(f"\n❌ Error: {e}", Colors.FAIL)
        for proc in processes:
            try:
                proc.kill()
            except:
                pass
        sys.exit(1)

if __name__ == '__main__':
    main()

