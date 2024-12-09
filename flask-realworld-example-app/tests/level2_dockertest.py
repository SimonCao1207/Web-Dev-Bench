import docker
import time
import tarfile
import io
import os
import subprocess
import sys

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
            detach=True,  # Run in detached mode to keep the container running
            tty=True
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

# Function to send commands to the subprocess
def send_command(command):
    # Write the command to the subprocess's stdin
    proc.stdin.write(command + '\n')
    proc.stdin.flush()  # Ensure the command is sent immediately

    # Read output line by line until the command completes
    while True:
        output = proc.stdout.readline()
        if output == '' and proc.poll() is not None:
            break
        if output:
            print(output.strip())  # Print the output from the command

path = "/Users/khuongle/Documents/web_bench/flask-realworld-example-app"
image_tag = "realworld"
container_name = "rw-container"
image = build_image(path, image_tag)
container = run_container(image_tag=image_tag, container_name=container_name)

# Start the interactive subprocess (e.g., a shell)
proc = subprocess.Popen(
    ['docker', 'exec', '-it', container_name, '/bin/bash'],  # Replace with your command, e.g., ['bash'] for a shell
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,  # Use text mode for string input/output
    bufsize=1   # Line-buffered
)
try:
    send_command("cd tests && python level2_test.py")  # Send the command to the subprocess
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    proc.terminate()  # Ensure the subprocess is terminated

# exec_result = container.exec_run("/bin/bash -c 'cd tests && python level2_test.py'")
# print(exec_result.output.decode('utf-8'))

result = fetch_logs(container)

# Copy the file from the container
# stream, stat = container.get_archive("test_level2_resp.json")

# # Extract the file content
# file_obj = io.BytesIO()
# for chunk in stream:
#     file_obj.write(chunk)
# file_obj.seek(0)

# # Extract the file from the tar archive
# with tarfile.open(fileobj=file_obj) as tar:
#     file_content = tar.extractfile(tar.getmembers()[0]).read()

# # Write the content to a local file
# with open(os.path.join(path, "test_level2_resp.json"), 'wb') as local_file:
#     local_file.write(file_content)

# container.stop()
# container.remove()
# client.images.remove(image=image_tag, force=True)