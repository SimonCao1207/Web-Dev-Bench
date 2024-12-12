import docker
import time
import tarfile
import io
import os
import subprocess
import sys

client = docker.from_env()

def build_image(dockerfile_path='.', dockerfile='Dockerfile', tag='my_image:latest'):
    try:
        print("Building the Docker image...")
        image, build_logs = client.images.build(path=dockerfile_path, dockerfile=dockerfile, tag=tag, rm=True)
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


def docker_test(path, dockerfile="Dockerfile.test"):
    image_tag = "realworld-test"
    container_name = "rw-container-test"
    file_path = "/app/custom_evaluation/test_level2_resp.json"
    image = build_image(path, dockerfile, image_tag)
    container = run_container(image_tag=image_tag, container_name=container_name)

    while True:
        exit_code, output = container.exec_run(f'test -f {file_path}')
        if exit_code == 0:
            break

    try:
        # Copy the file from the container
        stream, stat = container.get_archive(file_path)

        # Extract the file content
        file_obj = io.BytesIO()
        for chunk in stream:
            file_obj.write(chunk)
        file_obj.seek(0)

        # Extract the file from the tar archive
        with tarfile.open(fileobj=file_obj) as tar:
            file_content = tar.extractfile(tar.getmembers()[0]).read()

        # Write the content to a local file
        with open(os.path.join(path, "test_level2_resp.json"), 'wb') as local_file:
            local_file.write(file_content)
    except Exception as e:
        print(f"Exception {e}")
    finally:
        container.stop()
        container.remove()
        client.images.remove(image=image_tag, force=True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str)
    parser.add_argument("--dockerfile", type=str)
    args = parser.parse_args()

    if args.dockerfile:
        docker_test(args.path, args.dockerfile)
    else:
        docker_test(args.path)
