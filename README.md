Web-Dev Bench is a benchmark to evaluate LLM agents’ abilities on modern web backend development tasks with the most-used frameworks (Flask - Python, Django - Python, Spring Boot - Java, Laravel - PHP, Express.js - JS). 

We follow the ![SWE agent](https://swe-agent.com/latest/) and simulate a coding environment. In that environment, an agent could search, view, edit files, and submit the final codebase for evaluation.

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

- Choose sets of masked API ids and run the following script (currently supported for Flask-based web backend repo). This will generate a repository with the specified APIs masked.

    ```bash
    python realworld/flask_mask.py --api_ids <list_of_masked_API_ids>
    ```

## 👩‍💻 Inference


Run agent and generate patches:
```bash
python run.py \
  --model <model_name> \
  --data_path <path_to_task_instance_markdown_file> \
  --repo_path <path_to_local_repository> \
  --config_file <path_to_yaml_configuration_file> \
  --environment_setup <path_to_bash_script_for_web_repo_setup> \
  --apply_patch_locally

```

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

For level 2 evaluation, we try to simulate multiple users interacting with the website with their own trajectories and interleave those trajectories. We tries to make the final combined trajectory to cover as much cases as possible to validate the functionality and data integrity even when the API call is successful or failure.

How to build it: We use a while loop to prompt LLMs to generate the final trajectory. First, given the instructions, API documentation, and the current trajectory, the LLM is asked to continue develop the trajectory by generating more API calls satisfying our requirements. After that, we give the instructions, requirements, the API documentation, and the new combined trajectory, and ask the LLMs to verify if the new combined trajectory pass the requirements. If it does, stop the while loop, otherwise continue.

To evaluate, move the custom_evaluation directory inside the folder you want to evaluate, then run "python level2_dockertest.py" with a running docker. Then, the final result is stored in test_level2_resp.json in the evaluating directory including the number of correct tests with their corresponding responses.