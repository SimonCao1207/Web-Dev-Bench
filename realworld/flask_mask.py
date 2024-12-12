import ast
import os
from pathlib import Path
import shutil
import docker
import time
import subprocess
import json

client = docker.from_env()

def build_image(dockerfile_path='.', tag='my_image:latest'):
    try:
        print("Building the Docker image...")
        image, build_logs = client.images.build(path=dockerfile_path, tag=tag, rm=True)
        for log in build_logs:
            if 'stream' in log:
                print(log['stream'].strip())
        print(f"Image '{tag}' built successfully.")
        return image
    except docker.errors.BuildError as e:
        print("Error occurred while building the image:", e)
    except Exception as e:
        print("Unexpected error:", e)

# Step 2: Run the Docker container
def run_container(image_tag, container_name='my_container'):
    try:
        print(f"Running the container '{container_name}' from image '{image_tag}'...")
        container = client.containers.run(
            image_tag,
            name=container_name,
            detach=True  # Run in detached mode to keep the container running
        )
        print(f"Container '{container_name}' is running.")
        return container
    except docker.errors.ContainerError as e:
        print("Container error:", e)
    except docker.errors.ImageNotFound:
        print("Image not found.")
    except docker.errors.APIError as e:
        print("Docker API error:", e)

# Step 3: Fetch logs from the container
def fetch_logs(container):
    try:
        # Wait a moment to allow the container to produce logs (optional, depends on the application)
        time.sleep(10)
        
        print("Fetching logs from the container...")
        logs = container.logs().decode("utf-8")
        print("Container logs:\n", logs)
        return ("Running on" in logs and "(Press CTRL+C to quit)" in logs)
    except docker.errors.APIError as e:
        print("Docker API error when fetching logs:", e)
    except Exception as e:
        print("Unexpected error:", e)
    
    return False

def find_function(directory, function_name):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == function_name:
                            print(f"Found {function_name} in {file} at line {node.lineno}")

def find_function_calls(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Name):
                                print(f"Function call: {node.func.id} in {file}")

def create_file_with_dirs(file_path):
    path = Path(file_path)
    
    # Check if the parent directory exists
    if not path.parent.exists():
        # Create all intermediate directories
        path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create the file if it doesn't exist
    if not path.exists():
        path.touch()

def add_task_instance_prefix(api_ids):
    return f"""
    Objective:
    Develop and implement API endpoints for a Flask backend application.

    Task Details:
    The APIs to be implemented are identified by their unique IDs, as follows: {", ".join(map(str, api_ids))}. 
    Detailed descriptions of each API, including their purpose, endpoints, methods, 
    and expected behavior, are provided below in JSON format.

    Requirements:
    - Implement each API according to its description and specified behavior.
    - Ensure proper handling of request and response data using Flask conventions.
    - Use appropriate authentication and validation mechanisms where necessary.
    - Follow best practices for modular and maintainable code.
    
    """

def mask(in_dir, out_dir, api_ids, docker_path, image_tag="my_image_tag", container_name="my_container", image_remove=False):
    """
        api: dict(endpoint: str, method: str)
        * mask
        * docker run
    """
    if os.path.isdir(out_dir):
        print("directory existed")
        exit(0)
    
    if os.path.exists(os.path.join(in_dir, "API_documentation.json")) is False:
        print("API documentation not exist")
        exit(0)
    
    with open(os.path.join(in_dir, "API_documentation.json"), "r") as f:
        data = json.load(f)
        apis = [api for api in data["APIs"] if api["id"] in api_ids]

    for root, dirs, files in os.walk(in_dir):
        for file in files:
            in_file = os.path.join(root, file)
            out_file = os.path.join(out_dir, in_file.removeprefix(in_dir + '/'))
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.readlines()
                
                create_file_with_dirs(out_file)
                with open(out_file, 'w') as f:
                    masking = 0
                    for line in lines:
                        if masking == 1 and "def" in line:
                            masking = 2
                        elif masking == 2:
                            stripped = line.lstrip()
                            if len(stripped) == len(line):
                                masking = 0
                        else:
                            for api in apis:
                                if api["endpoint"] in line and api["method"] in line:
                                    masking = 1
                                    if "def" in line:
                                        masking = 2
                        
                        if masking == 0:
                            f.write(line)
            elif file == "API_documentation.json":
                with open(in_file, "r") as f:
                    data = json.load(f)
                    for api in data["APIs"]:
                        if api["id"] not in api_ids and "samples" in api:
                            del api["samples"]
                
                comps = out_file.split("/")
                comps[-1] = "README.md"
                out_file = "/".join(comps)
                print(out_file)
                create_file_with_dirs(out_file)
                with open(out_file, 'w') as md_file:
                    md_file.write(add_task_instance_prefix(api_ids))
                    md_file.write("```json\n")
                    md_file.write(json.dumps(data, indent=4, sort_keys=True))
                    md_file.write("\n```")
            else:
                create_file_with_dirs(out_file)
                shutil.copyfile(in_file, out_file)

    subprocess.run(['git', 'init'], cwd=out_dir, check=True)
    subprocess.run(['git', 'add', '.'], cwd=out_dir, check=True)
    subprocess.run(['git', 'commit', '-m', 'init'], cwd=out_dir, check=True)
    
    # image = build_image(docker_path, image_tag)
    # container = run_container(image_tag=image_tag, container_name=container_name)
    
    result = False

    # if container:
    #     result = fetch_logs(container)
    #     # Stop and remove the container after logs are fetched
    #     container.stop()
    #     container.remove()
    #     print(f"Container '{container_name}' has been stopped and removed.")
    
    # if image_remove:
    #     client.images.remove(image=image_tag, force=True)
    #     print(f"Image '{image_tag}' has been removed.")

    return result

import argparse
parser = argparse.ArgumentParser(description="Mask APIs in a web application directory.")
parser.add_argument(
    '--api_ids', 
    nargs='+',  # Allow multiple API IDs as a list
    required=True, 
    help="List of API IDs to be masked"
)
args = parser.parse_args()

original_dir = '/root/web_bench/flask-realworld-example-app'
dup_dir = f"/root/web_bench/realworld_masked/attempt{'_'.join(args.api_ids)}"
docker_dir = dup_dir
print(mask(original_dir, dup_dir, args.api_ids, docker_dir, image_remove=True))
