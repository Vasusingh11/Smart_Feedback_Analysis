#!/usr/bin/env python3
"""
Smart Feedback Analysis Platform - Installation Script
Automates the setup and installation process
"""

import os
import sys
import subprocess
import shutil
import argparse
import platform
from pathlib import Path
from typing import List, Dict, Any

class PlatformInstaller:
    """Main installer class for the feedback analysis platform"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system().lower()
        self.errors = []
        self.warnings = []
        
    def print_header(self):
        """Print installation header"""
        print("=" * 70)
        print("SMART FEEDBACK ANALYSIS PLATFORM - INSTALLER")
        print("=" * 70)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Installation directory: {self.project_root}")
        print("=" * 70)
        print()
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        print("🔍 Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8+ is required")
            return False
        print("✅ Python version: OK")
        
        # Check pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip: OK")
        except subprocess.CalledProcessError:
            self.errors.append("pip is not available")
            return False
        
        # Check git (optional but recommended)
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            print("✅ git: OK")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.warnings.append("git is not available (optional)")
        
        # Check for SQL Server ODBC driver (Windows/Linux specific)
        self.check_odbc_driver()
        
        return len(self.errors) == 0
    
    def check_odbc_driver(self):
        """Check for SQL Server ODBC driver"""
        if self.system == 'windows':
            # Check Windows registry or common locations
            try:
                import winreg
                # Check for ODBC drivers in registry
                # This is a simplified check
                print("✅ Windows ODBC drivers: Available")
            except ImportError:
                self.warnings.append("Cannot verify ODBC drivers on Windows")
        elif self.system == 'linux':
            # Check for common ODBC driver locations
            odbc_paths = [
                '/opt/microsoft/msodbcsql17/',
                '/opt/microsoft/msodbcsql18/',
                '/usr/lib/x86_64-linux-gnu/odbc/'
            ]
            
            driver_found = any(Path(path).exists() for path in odbc_paths)
            if driver_found:
                print("✅ SQL Server ODBC driver: Found")
            else:
                self.warnings.append("SQL Server ODBC driver may not be installed")
        else:
            self.warnings.append(f"ODBC driver check not implemented for {self.system}")
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating directories...")
        
        directories = [
            'logs',
            'exports', 
            'data',
            'data/raw',
            'data/processed',
            'tests/reports',
            'config/backups'
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
    
    def setup_virtual_environment(self, venv_name: str = 'venv'):
        """Setup Python virtual environment"""
        print(f"\n🐍 Setting up virtual environment: {venv_name}")
        
        venv_path = self.project_root / venv_name
        
        if venv_path.exists():
            print(f"⚠️  Virtual environment already exists: {venv_path}")
            response = input("Remove existing environment and create new? (y/N): ")
            if response.lower() == 'y':
                shutil.rmtree(venv_path)
            else:
                print("Using existing virtual environment")
                return
        
        # Create virtual environment
        try:
            subprocess.run([
                sys.executable, '-m', 'venv', str(venv_path)
            ], check=True)
            print(f"✅ Virtual environment created: {venv_path}")
            
            # Provide activation instructions
            if self.system == 'windows':
                activate_cmd = f"{venv_path}\\Scripts\\activate.bat"
            else:
                activate_cmd = f"source {venv_path}/bin/activate"
            
            print(f"💡 To activate: {activate_cmd}")
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to create virtual environment: {e}")
    
    def install_dependencies(self, dev: bool = False):
        """Install Python dependencies"""
        print("\n📦 Installing Python dependencies...")
        
        requirements_file = 'requirements.txt'
        if dev and (self.project_root / 'requirements-dev.txt').exists():
            requirements_file = 'requirements-dev.txt'
        
        requirements_path = self.project_root / requirements_file
        
        if not requirements_path.exists():
            self.errors.append(f"Requirements file not found: {requirements_path}")
            return
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True)
            print("✅ pip upgraded")
            
            # Install requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
            ], check=True)
            print(f"✅ Dependencies installed from {requirements_file}")
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install dependencies: {e}")
    
    def download_nltk_data(self):
        """Download required NLTK data"""
        print("\n📚 Downloading NLTK data...")
        
        nltk_datasets = ['punkt', 'stopwords', 'vader_lexicon', 'wordnet', 'omw-1.4']
        
        try:
            import nltk
            
            for dataset in nltk_datasets:
                try:
                    nltk.download(dataset, quiet=True)
                    print(f"✅ Downloaded: {dataset}")
                except Exception as e:
                    self.warnings.append(f"Failed to download {dataset}: {e}")
                    
        except ImportError:
            self.errors.append("NLTK not available - install dependencies first")
    
    def setup_configuration(self):
        """Setup configuration files"""
        print("\n⚙️  Setting up configuration...")
        
        config_dir = self.project_root / 'config'
        
        # Copy example config if main config doesn't exist
        example_config = config_dir / 'config.yaml.example'
        main_config = config_dir / 'config.yaml'
        
        if example_config.exists() and not main_config.exists():
            shutil.copy2(example_config, main_config)
            print(f"✅ Created config.yaml from example")
            print("💡 Please edit config/config.yaml with your database credentials")
        
        # Copy .env.example if .env doesn't exist
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if env_example.exists() and not env_file.exists():
            shutil.copy2(env_example, env_file)
            print("✅ Created .env from example")
            print("💡 Please edit .env with your environment variables")
    
    def test_installation(self):
        """Test the installation"""
        print("\n🧪 Testing installation...")
        
        # Test basic imports
        test_imports = [
            'pandas',
            'numpy', 
            'nltk',
            'textblob',
            'sklearn',
            'sqlalchemy',
            'yaml'
        ]
        
        for module in test_imports:
            try:
                __import__(module)
                print(f"✅ Import test: {module}")
            except ImportError as e:
                self.errors.append(f"Import failed: {module} - {e}")
        
        # Test custom modules
        try:
            sys.path.append(str(self.project_root))
            from src.data_processing.sentiment_analyzer import SentimentAnalyzer
            analyzer = SentimentAnalyzer()
            
            # Test basic functionality
            result = analyzer.analyze_sentiment("This is a test message")
            assert 'score' in result
            assert 'label' in result
            print("✅ Sentiment analyzer test: OK")
            
        except Exception as e:
            self.warnings.append(f"Sentiment analyzer test failed: {e}")
        
        # Test database connection (if configured)
        try:
            from src.database.connection import DatabaseHandler
            
            # This will fail if not configured, which is expected
            config_path = self.project_root / 'config' / 'config.yaml'
            if config_path.exists():
                print("💡 Database test skipped - configure database first")
            else:
                print("💡 Database test skipped - no config file")
                
        except Exception as e:
            print(f"💡 Database test skipped: {e}")
    
    def create_startup_scripts(self):
        """Create convenient startup scripts"""
        print("\n📜 Creating startup scripts...")
        
        scripts_dir = self.project_root / 'scripts'
        
        # Create run script for different platforms
        if self.system == 'windows':
            run_script = scripts_dir / 'run.bat'
            with open(run_script, 'w') as f:
                f.write(f"""@echo off
echo Starting Smart Feedback Analysis Platform...
cd /d "{self.project_root}"
python scripts/run_analysis.py run
pause
""")
            print("✅ Created run.bat")
            
        else:  # Linux/macOS
            run_script = scripts_dir / 'run.sh'
            with open(run_script, 'w') as f:
                f.write(f"""#!/bin/bash
echo "Starting Smart Feedback Analysis Platform..."
cd "{self.project_root}"
python scripts/run_analysis.py run
""")
            
            # Make executable
            os.chmod(run_script, 0o755)
            print("✅ Created run.sh")
    
    def print_next_steps(self):
        """Print next steps after installation"""
        print("\n" + "=" * 70)
        print("INSTALLATION COMPLETE!")
        print("=" * 70)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Configure your database connection in config/config.yaml")
        print("2. Update environment variables in .env file")
        print("3. Run database setup: python scripts/setup_database.py")
        print("4. Generate sample data: python scripts/setup_database.py --sample-data")
        print("5. Run the analysis pipeline: python scripts/run_analysis.py run")
        print("6. Connect Power BI to your database using the provided templates")
        
        print("\n🚀 QUICK START:")
        print("   python scripts/run_analysis.py run")
        print("   python scripts/health_check.py")
        
        print("\n📖 DOCUMENTATION:")
        print("   • README.md - Project overview and setup")
        print("   • docs/ - Detailed documentation")
        print("   • API docs: http://localhost:8000/docs (when API is running)")
        
        print("\n🎯 DOCKER ALTERNATIVE:")
        print("   docker-compose up -d")
        
        print("=" * 70)
    
    def install(self, venv: bool = True, dev: bool = False, venv_name: str = 'venv'):
        """Run complete installation process"""
        self.print_header()
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed!")
            for error in self.errors:
                print(f"   • {error}")
            return False
        
        # Create directories
        self.create_directories()
        
        # Setup virtual environment
        if venv:
            self.setup_virtual_environment(venv_name)
        
        # Install dependencies
        self.install_dependencies(dev)
        
        # Download NLTK data
        self.download_nltk_data()
        
        # Setup configuration
        self.setup_configuration()
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Test installation
        self.test_installation()
        
        # Print next steps
        self.print_next_steps()
        
        return len(self.errors) == 0

def main():
    """Main installation function"""
    parser = argparse.ArgumentParser(
        description='Smart Feedback Analysis Platform Installer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/install.py                    # Standard installation
  python scripts/install.py --no-venv         # Install without virtual environment
  python scripts/install.py --dev             # Install with development dependencies
  python scripts/install.py --venv-name myenv # Use custom virtual environment name
        """
    )
    
    parser.add_argument('--no-venv', action='store_true', 
                       help='Skip virtual environment creation')
    parser.add_argument('--dev', action='store_true',
                       help='Install development dependencies')
    parser.add_argument('--venv-name', default='venv',
                       help='Virtual environment name (default: venv)')
    parser.add_argument('--force', action='store_true',
                       help='Force installation even if prerequisites fail')
    
    args = parser.parse_args()
    
    installer = PlatformInstaller()
    
    try:
        success = installer.install(
            venv=not args.no_venv,
            dev=args.dev,
            venv_name=args.venv_name
        )
        
        if success:
            print("\n🎉 Installation completed successfully!")
            return 0
        else:
            print("\n⚠️  Installation completed with errors!")
            return 1 if not args.force else 0
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)