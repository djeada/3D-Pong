"""
Build script for 3D Pong game.

This script builds standalone executables for the 3D Pong game using Nuitka.
It supports Windows, macOS, and Linux platforms.

Usage:
    python build.py [--install-deps]

Options:
    --install-deps  Install Python dependencies before building
"""

import subprocess
import sys
import logging
import multiprocessing
import platform
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def run_command(command, timeout=3600, check=False):
    """Run a system command with a timeout and log the output."""
    logging.info(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=timeout,
                                check=check)
        logging.info(result.stdout.decode())
        if result.returncode != 0:
            logging.error(
                f"Command failed with return code {result.returncode}")
            logging.error(result.stderr.decode())
        return result.returncode
    except subprocess.TimeoutExpired:
        logging.error(
            f"Command {' '.join(command)} timed out after {timeout} seconds")
        return -1
    except subprocess.CalledProcessError as e:
        logging.error(f"Command {' '.join(command)} failed with error: {e}")
        return e.returncode


def install_dependencies():
    """Install required Python packages."""
    logging.info("Installing Python dependencies...")
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    run_command([sys.executable, '-m', 'pip', 'install', 'nuitka'])
    logging.info("Dependencies installed successfully.")


def get_output_filename():
    """Get the appropriate output filename based on the platform."""
    system = platform.system().lower()
    if system == 'windows':
        return '3D-Pong.exe'
    return '3D-Pong'


def build():
    """Build the standalone executable using Nuitka."""
    num_cores = multiprocessing.cpu_count()
    logging.info(f"Number of available CPU cores: {num_cores}")

    output_filename = get_output_filename()
    logging.info(f"Building for platform: {platform.system()}")
    logging.info(f"Output filename: {output_filename}")

    # Platform-specific timeout values (in seconds)
    # macOS builds with VTK and --onefile are significantly slower
    system = platform.system().lower()
    if system == 'darwin':
        timeout = 7200  # 2 hours for macOS
    else:
        timeout = 3600  # 1 hour for Linux and Windows

    logging.info(f"Build timeout set to {timeout} seconds ({timeout/60:.0f} minutes)")

    # Nuitka compilation command
    nuitka_command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--assume-yes-for-downloads",
        "--include-package=vtkmodules",
        "--include-module=vtk",
        "--include-module=vtkmodules.all",
        "--nofollow-import-to=vtkmodules.test",
        f"--output-filename={output_filename}",
        f"--jobs={num_cores}",
        "src/main.py"
    ]

    logging.info(f"Running Nuitka compilation: {' '.join(nuitka_command)}")
    return_code = run_command(nuitka_command, timeout=timeout, check=True)

    if return_code == 0:
        logging.info(f"Build completed successfully! Executable: {output_filename}")
    else:
        logging.error("Build failed!")
        sys.exit(1)


def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(description='Build 3D Pong executable')
    parser.add_argument('--install-deps', action='store_true',
                        help='Install Python dependencies before building')
    args = parser.parse_args()

    if args.install_deps:
        install_dependencies()

    build()


if __name__ == "__main__":
    main()
