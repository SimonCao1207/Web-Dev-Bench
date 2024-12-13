Web-Dev Bench is a benchmark to evaluate LLM agents’ abilities on modern web backend development tasks with the most-used frameworks (Flask - Python, Django - Python, Spring Boot - Java, Laravel - PHP, Express.js - JS). 

We follow the ![SWE agent](https://github.com/SWE-agent/SWE-agent) and simulate a coding environment. In that environment, an agent could search, view, edit files, and submit the final codebase for evaluation.

The Web-Dev-Bench pipeline consists of two steps. First, the agent processes an input task instance and generates a local patch aimed at addressing the issue—this step is called inference. The second step involves evaluating the patch to ensure that it successfully completes the task instance.

## 👩‍💻 Inference

Run agent and generate patches.

## 🧪 Evaluation

