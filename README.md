# Web-Dev Benchmarking
Web-Dev Bench is a benchmark to evaluate LLM agents’ abilities on modern web backend development tasks with the most-used frameworks (Flask - Python, Django - Python, Spring Boot - Java, Laravel - PHP, Express.js - JS).

We follow the <a href="https://swe-agent.com/latest/"><strong>SWE agent</strong></a> and simulate a coding environment. In that environment, an agent could search, view, edit files, and submit the final codebase for evaluation.

The Web-Dev-Bench pipeline consists of two steps. First, the agent processes an input task instance and generates a local patch aimed at addressing the issue—this step is called inference. The second step involves evaluating the patch to ensure that it successfully completes the task instance.

## Prepare
### 1. API Documentation Extraction
Extract API documentation from a web backend development repository and convert it into JSON format for easy retrieval by the agent.
- Example : 
```bash

    {
        "description": "User login. Return an User if the email and password matched any record in the data. Otherwise return \"User not found\".\n",
        "endpoint": "/api/users/login",
        "id": 0,
        "method": "POST"
    },
    ...
```
### 2. APIs Masking
- To formulate a task for the agent, randomly mask implemented APIs from the original codebase of the repository.
- Tasks are categorized into multiple levels by the number of masked APIs (1 API, 10% APIs, 20% APIs, 50% APIs, 100% APIs).

- Select a set of masked API IDs and run the script below (currently only supported for Flask-based web backend repositories). This will generate a repository with the specified APIs masked.

    ```bash
    python realworld/flask_mask.py --api_ids <list_of_masked_API_ids>
    ```

## 👩‍💻 Inference

### 1. Create human demonstration trajectory:
- An important way to show LMs how to use commands and interact with the environment is through providing a demonstration - which is basically a completed `trajectory` that the LM can learn from.
- We manually generate a trajectory by running the agent with flag `--model human_thought` in the following script.
```bash
python run.py \
  --model <model_name> \
  --data_path <path_to_task_instance_markdown_file> \
  --repo_path <path_to_local_repository> \
  --config_file <path_to_yaml_configuration_file> \
  --environment_setup <path_to_bash_script_for_web_repo_setup> \

```
### 2. Run agent and generate patches:


- Example: 
```bash
python run.py \
  --model berkeley/llama \
  --data_path /root/web_bench/realworld_masked/attempt0/README.md \
  --repo_path /root/web_bench/realworld_masked/attempt0 \
  --config_file config/default_web_dev.yaml \
  --environment_setup config/environment_setup/realworld_flask.sh \
  --apply_patch_locally
```


## 🧪 Evaluation

### Level 1 test (already provided)
- These unit tests, commonly found in most web backend repositories, ensure API correctness and security under various conditions. Run `pytest` to run the unit tests. 
- A test case passes if the last API response has:
    - Correct Response Codes: Expected status codes (e.g., 200, 404).
    - Valid Structure and Contents: Proper format (e.g., JSON) with all required fields.
- Essential Test Scenarios:
    - Boundary Cases: Missing fields, invalid data (e.g., non-email, null), exceeding limits (e.g., large strings), and unsupported methods.
    - Authentication: Access without credentials, expired/invalid tokens, or unauthorized roles.

### Level 2 test (LLM generated)

- For level 2 evaluation, we try to simulate multiple users interacting with the website with their own trajectories and interleave those trajectories. We tries to make the final combined trajectory to cover as much cases as possible to validate the functionality and data integrity even when the API call is successful or failure.

- How to build it: 
    - We use a while loop to prompt LLMs to generate the final trajectory. First, given the instructions, API documentation, and the current trajectory, the LLM is asked to continue develop the trajectory by generating more API calls satisfying our requirements. 
    - After that, we give the instructions, requirements, the API documentation, and the new combined trajectory, and ask the LLMs to verify if the new combined trajectory pass the requirements. If it does, stop the while loop, otherwise continue.

- To evaluate, move the `custom_evaluation` directory inside the folder you want to evaluate, then run the following script with a running docker.
    ```bash
    python level2_dockertest.py
    ```
- Then, the final result is stored in `test_level2_resp.json` in the evaluating directory including the number of correct tests with their corresponding responses.
    - Example: 
    ```bash
     {
        "request_id": 0,
        "status_code": 200,
        "reason": "OK",
        "data": {
            "user": {
                "bio": null,
                "email": "testuser1@example.com",
                "image": null,
                "username": "testuser1"
            }
        }
    },
    {
        "request_id": 1,
        "status_code": 200,
        "reason": "OK",
        "data": {
            "user": {
                "bio": null,
                "email": "testuser2@example.com",
                "image": null,
                "username": "testuser2"
            }
        }
    },
    ...
    ```

## Experiment
### 1. Repository selection
- There are two sources for us to choose repositories which are <a href="https://github.com/gothinkster/realworld">realworld</a> and <a href="https://github.com/sdil/open-production-web-projects">open-source repositories</a>. 
### 2. Result
- We experimented the pipeline with <a href="https://github.com/gothinkster/flask-realworld-example-app">flask-realworld-example-app
</a> which is a Flask-base medium-sized repository and contains all fundamental concepts of back-end web developments. 
- We test 19 instances, each masking one of 19 APIs. The model agent used is `llama3.1-70b-instruct-berkeley`. Only 2 of the 19 APIs are correctly implemented in the appropriate location, and only one passes the level 1 unit tests.

### 3. Discussion
- The agent struggles with identifying the correct implementation location and navigating through separate database model files to implement the API accurately.
