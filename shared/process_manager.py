import subprocess
import os
import sys


def spawn_user_instance(user_id: int, port: int) -> subprocess.Popen:
    """
    Spawn a new FastAPI instance for a user.
    
    Args:
        user_id: The user ID
        port: The port to run on
    
    Returns:
        The Popen object representing the process
    """
    # Get the path to the user instance app
    user_app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "user_instances",
        "user_instance_app.py"
    )
    
    # Setup environment variables
    env = os.environ.copy()
    env["USER_ID"] = str(user_id)
    env["PORT"] = str(port)
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Start the process
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            f"user_instances.user_instance_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    return process


def spawn_driver_instance(driver_id: int, port: int) -> subprocess.Popen:
    """
    Spawn a new FastAPI instance for a driver.
    
    Args:
        driver_id: The driver ID
        port: The port to run on
    
    Returns:
        The Popen object representing the process
    """
    # Get the path to the driver instance app
    driver_app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "driver_instances",
        "driver_instance_app.py"
    )
    
    # Setup environment variables
    env = os.environ.copy()
    env["DRIVER_ID"] = str(driver_id)
    env["PORT"] = str(port)
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Start the process
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            f"driver_instances.driver_instance_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    return process
