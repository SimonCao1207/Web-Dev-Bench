import json
import re
import requests
import copy

with open('level2.json', 'r') as f:
    apis = json.load(f)
with open('level2_resp.json', 'r') as f:
    ans = json.load(f)

prefix = "http://127.0.0.1:5000"
responses = []
correct = 0
keywords = ["token", "createdAt", "updatedAt"]
for api in apis:
    headers = {}
    
    if "dependencies" in api.keys():
        ids = re.findall(r'\d+', api["dependencies"]["token"])
        if len(ids) > 0:
            try:
                output = responses[int(ids[0])]["data"]
                headers = {
                    'Authorization': 'Token {}'.format(output["user"]["token"])
                }
            except Exception as e:
                print(ids[0], api)

    if "slug" in api["input"].keys():
        api["api_endpoint"] = api["api_endpoint"].replace(":slug", api["input"]["slug"])
        del api["input"]["slug"]
    
    api["api_endpoint"] = prefix + api["api_endpoint"]

    resp = {}
    if api["method"] == "POST":
        resp = requests.post(api["api_endpoint"], json=api["input"], headers=headers)
    elif api["method"] == "GET":
        resp = requests.get(api["api_endpoint"], headers=headers)
    elif api["method"] == "PUT":
        resp = requests.put(api["api_endpoint"], json=api["input"], headers=headers)
    elif api["method"] == "DELETE":
        resp = requests.delete(api["api_endpoint"], headers=headers)
    else:
        raise Exception("unexpected method {}".format(api["method"]))

    formatted_resp = {
        "request_id": api["request_id"],
        "status_code": resp.status_code,
        "reason": resp.reason,
        "data": resp.json() if resp.ok and api["method"] != "DELETE" else {},
    }

    responses.append(formatted_resp)

for resp in responses:
    for kw in keywords:
        def delete(data, kw):
            if isinstance(data, dict):
                if kw in data:
                    del data[kw]
                for k in data:
                    delete(data[k], kw)
            elif isinstance(data, list):
                for d in data:
                    delete(d, kw)
        delete(resp["data"], kw)
    
    if resp == ans[resp["request_id"]]:
        correct += 1
    else:
        print("response: ", resp)
        print("result: ", ans[resp["request_id"]])

output = {
    "correct_apis": correct,
    "responses": responses
}

with open('test_level2_resp.json', 'w') as f:
    json.dump(output, f, indent=4)