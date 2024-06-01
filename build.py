import subprocess
import os
import shutil
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import sys

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def run_command(command, timeout=1800, check=False):
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
    """Install required packages and tools."""
    if os.geteuid() != 0:
        logging.error(
            "This script requires sudo privileges. Please run as root.")
        sys.exit(1)
    run_command(['apt-get', 'update'])
    run_command(
        ['apt-get', 'install', '-y', 'ccache', 'wget', 'build-essential',
         'libssl-dev', 'zlib1g-dev',
         'libbz2-dev', 'libreadline-dev', 'libsqlite3-dev', 'llvm',
         'libncurses5-dev', 'libncursesw5-dev',
         'xz-utils', 'tk-dev', 'libffi-dev', 'liblzma-dev', 'python3-openssl',
         'git'])
    run_command(['python3', '-m', 'pip', 'install', '--upgrade', 'pip'])
    run_command(['python3', '-m', 'pip', 'install', 'nuitka', 'vtk'])


def recompile_python():
    """Recompile Python with static linking."""
    python_version = '3.10.5'
    python_tar = f'Python-{python_version}.tgz'
    python_dir = f'Python-{python_version}'

    if not os.path.exists(python_tar):
        run_command(['wget',
                     f'https://www.python.org/ftp/python/{python_version}/{python_tar}'])
    if not os.path.exists(python_dir):
        run_command(['tar', 'xzf', python_tar])
    os.chdir(python_dir)
    run_command(['./configure', '--enable-optimizations', '--with-lto',
                 '--enable-shared'])
    run_command(['make', '-j', str(multiprocessing.cpu_count())])
    run_command(['sudo', 'make', 'altinstall'], check=True)
    os.chdir('..')


def get_shared_libs(binary):
    """Get shared libraries required by a binary."""
    logging.info(f"Getting shared libraries for {binary}")
    result = subprocess.run(['ldd', binary], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    lines = result.stdout.decode().split('\n')
    libs = set()
    for line in lines:
        parts = line.strip().split('=>')
        if len(parts) == 2:
            lib_path = parts[1].strip().split(' ')[0]
            if os.path.exists(lib_path):
                libs.add(lib_path)
    return libs


def gather_vtk_shared_libs():
    """Gather shared libraries for VTK modules."""
    import vtk
    vtk_libs = set()
    vtk_modules = [
        'vtkCommonCore', 'vtkCommonDataModel', 'vtkCommonExecutionModel',
        'vtkFiltersCore', 'vtkFiltersGeometry', 'vtkFiltersSources',
        'vtkInteractionStyle', 'vtkRenderingCore', 'vtkRenderingOpenGL2'
    ]
    for module_name in vtk_modules:
        try:
            module = getattr(vtk, module_name)
            vtk_libs.update(get_shared_libs(module.__file__))
        except AttributeError as e:
            logging.warning(f"Module {module_name} not found: {e}")
    return vtk_libs


def copy_lib(lib, target_dir):
    """Copy a single library to the target directory."""
    target_path = os.path.join(target_dir, os.path.basename(lib))
    if not os.path.exists(target_path):
        logging.info(f"Copying {lib} to {target_dir}")
        shutil.copy(lib, target_dir)
    else:
        logging.info(f"{lib} already exists in {target_dir}")


def copy_libs_to_directory(libs, target_dir):
    """Copy shared libraries to the target directory using parallel execution."""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    with ThreadPoolExecutor() as executor:
        for lib in libs:
            executor.submit(copy_lib, lib, target_dir)


def main():
    if os.geteuid() != 0:
        logging.error(
            "This script requires sudo privileges. Please run as root.")
        sys.exit(1)
    install_dependencies()
    recompile_python()

    target_dir = "./vtk_libs"
    if not os.path.exists(target_dir) or not os.listdir(target_dir):
        logging.info("Gathering VTK shared libraries...")
        vtk_libs = gather_vtk_shared_libs()
        # Adding Python shared library
        python_lib = get_shared_libs(sys.executable)
        vtk_libs.update(python_lib)
        copy_libs_to_directory(vtk_libs, target_dir)
        logging.info("Shared libraries copied.")
    else:
        logging.info("Shared libraries already exist, skipping copy step.")

    # Determine number of available CPU cores
    num_cores = multiprocessing.cpu_count()
    logging.info(f"Number of available CPU cores: {num_cores}")

    # Nuitka compilation command
    nuitka_command = [
        "python3", "-m", "nuitka", "--standalone", "--onefile",
        "--plugin-enable=numpy",
        "--include-package=vtkmodules",
        "--include-module=vtk",
        "--include-module=vtkmodules.all",
        "--follow-imports",
        f"--include-data-dir={target_dir}={target_dir}",
        f"--jobs={num_cores}", "src/main.py"
    ]

    logging.info(f"Running Nuitka compilation: {' '.join(nuitka_command)}")
    run_command(nuitka_command, timeout=1800,
                check=True)  # Extended timeout to 30 minutes


if __name__ == "__main__":
    main()
