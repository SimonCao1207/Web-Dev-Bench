import os
import json

in_dir = "/Users/khuongle/Documents/web_bench/flask-realworld-example-app/API_documentation.txt"
out_dir = "/Users/khuongle/Documents/web_bench/flask-realworld-example-app/API_documentation.json"

with open(in_dir, 'r') as f:
    lines = f.readlines()

output = list()
cur_api = dict()
for line in lines:
    if line[0] >= '0' and line[0] <= '9':
        if len(cur_api.keys()) > 0:
            output.append(cur_api)
        cur_api = dict()
        cur_api["samples"] = []
        cur_api["id"] = len(output)
    elif line.startswith(tuple(["GET", "POST", "PUT", "DELETE", "PATCH"])):
        info = line.split(" ")
        cur_api["method"] = info[0]
        cur_api["endpoint"] = info[1].replace("\n", "")
    elif line.startswith("Sample request"):
        info = line.split(" - ")
        cur_api["samples"].append({
            "id": len(cur_api["samples"]),
            "request": info[0][len("Sample request  "):],
            "response": "" if len(info) <= 1 else json.loads(info[1][len("Sample response: "):]),
        })
    elif line != "\n":
        cur_api["description"] = line

if len(cur_api.keys()) > 0:
    output.append(cur_api)

with open(out_dir, 'w') as f:
    json.dump(output, f, indent=4)