import os
import json
import re
import glob

def grep_status(folder_path):
    model_name = None
    scenario = None
    if "bert" in folder_path:
        model_name = "bert"
    elif "resnet50" in folder_path:
        model_name = "resnet50"
    elif "retinanet" in folder_path:
        model_name = "retinanet"
    if "singlestream" in folder_path:
        scenario = "singlestream"
    elif "multistream" in folder_path:
        scenario = "multistream"
    elif "offline" in folder_path:
        scenario = "offline"
    elif "server" in folder_path:
        scenario = "server"

    if scenario == "offline" or scenario == "server":
        qps_or_latency = "target_qps"
    else:
        qps_or_latency = "target_latency"
        
    import re

    regex_target = r"(target_latency\.(\d+\.\d+|\.\d+|\d+)|target_qps\.(\d+\.\d+|\.\d+|\d+))"

    match = re.search(regex_target, folder_path)

    if match:
        # get the matched group
        number = match.group(2) or match.group(3)
    else:
        print("No match found for qps_or_latency")
    # print(model_name, scenario, qps_or_latency, number)
    return model_name, scenario, qps_or_latency, number

patterns = {
    "offline": r"\bSamples per second\s?:\s+(\d+(\.\d+)?)?\b",
    "server": r"\bScheduled samples per second\s?:\s+(\d+\.\d+)\b",
    "singlestream": r"\b90th percentile latency \(ns\) : (\d+)\b",
    "multistream": r"\b99th percentile latency \(ns\) : (\d+)\b"
}

regex_target = r"(target_latency\.(\d+\.\d+|\.\d+)|target_qps\.(\d+\.\d+|\.\d+))"

def grep_value(folder_path, patterns):
    filenames = glob.glob(folder_path + "*json")
    model_name, scenario, qps_or_latency, number = grep_status(folder_path)
    for file_path in filenames:
        if file_path.endswith("0001.json"):
            with open(file_path) as f:
                json_dict = json.load(f)
                avg_power = None
                if "characteristics_list" in json_dict and len(json_dict["characteristics_list"]) > 0:
                    run = json_dict["characteristics_list"][0].get("run")
                    if run:
                        avg_power = run.get("avg_power")
            with open(file_path) as f:
                lines = f.readlines()
                pattern = patterns[scenario]
                for line in lines:
                    match = re.search(pattern, line)
                    if match:
                        return model_name, scenario, match.group(1), qps_or_latency, number, avg_power
            return None

experiment_path = "experiment/"
folders = glob.glob(experiment_path + "*")

for folder_path in folders:
    if "accuracy" in folder_path or "TEST" in folder_path:
        continue # skip this folder and continue with the next one
    folder_path += "/"
    # print(folder_path)
    model_name, scenario, value, qps_or_latency, number, avg_power = grep_value(folder_path, patterns)
    if scenario == "singlestream":
        if value is not None:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - 90th percentile latency (ns): {value} Avg_power:{avg_power} ")
        else:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - 90th percentile latency (ns) not found. Avg_power:{avg_power} ")
    elif scenario == "offline" or scenario == "server":
        if value is not None:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - Samples per second: {value} Avg_power:{avg_power}")
        else:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - Samples per second not found. Avg_power:{avg_power}")
    elif scenario == "multistream":
        if value is not None:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - 99th percentile latency (ns): {value}. Avg_power:{avg_power} ")
        else:
            print(f"{model_name} {scenario} {qps_or_latency} {number} - 99th percentile latency (ns) not found. Avg_power:{avg_power} ")
