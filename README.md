Web-Dev Bench is a benchmark to evaluate LLM agents’ abilities on modern web backend development tasks with the most-used frameworks (Flask - Python, Django - Python, Spring Boot - Java, Laravel - PHP, Express.js - JS). 

We follow the ![SWE agent](https://github.com/SWE-agent/SWE-agent) and simulate a coding environment. In that environment, an agent could search, view, edit files, and submit the final codebase for evaluation.

The Web-Dev-Bench pipeline consists of two steps. First, the agent processes an input task instance and generates a local patch aimed at addressing the issue—this step is called inference. The second step involves evaluating the patch to ensure that it successfully completes the task instance.

## 👩‍💻 Inference

Run agent and generate patches.

## 🧪 Evaluation

For level 2 evaluation, we try to simulate multiple users interacting with the website with their own trajectories and interleave those trajectories. We tries to make the final combined trajectory to cover as much cases as possible to validate the functionality and data integrity even when the API call is successful or failure.

How to build it: We use a while loop to prompt LLMs to generate the final trajectory. First, given the instructions, API documentation, and the current trajectory, the LLM is asked to continue develop the trajectory by generating more API calls satisfying our requirements. After that, we give the instructions, requirements, the API documentation, and the new combined trajectory, and ask the LLMs to verify if the new combined trajectory pass the requirements. If it does, stop the while loop, otherwise continue.

To evaluate, move the custom_evaluation directory inside the folder you want to evaluate, then run "python level2_dockertest.py" with a running docker. Then, the final result is stored in test_level2_resp.json in the evaluating directory including the number of correct tests with their corresponding responses.