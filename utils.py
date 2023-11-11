import configparser
import requests
import re
import json
import os

def read_config(Section, key, file_path = './config.ini'):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')

    # 检查指定的 section 和 key 是否存在于配置文件中
    if config.has_section(Section) and config.has_option(Section, key):
        value = config.get(Section, key)
        return value
    else:
        return None

def call_openai_api(payload, url, api_key, proxy = None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, headers=headers, json=payload, proxies=proxy)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.text)
            return {"error": "Failed to call the OpenAI API"}
    except Exception as e:
        return {"error": f"An error occurred while calling the OpenAI API: {str(e)}"}

def update_token_count(file_name, token_count):#更新Token计数
    try:
        # Read the current token count from the file
        with open(file_name, 'r') as file:
            current_token_count = int(file.read().strip())
    except FileNotFoundError:
        current_token_count = 0
    # Calculate the new total token count
    new_token_count = current_token_count + token_count
    # Write the new total token count back to the file (overwrite the file)
    with open(file_name, 'w') as file:
        file.write(str(new_token_count))
    # Print the usage information
    print(f"Token usage: {token_count}  Total tokens used: {new_token_count}")

def parse_cq_codes(text):#解析CQ码
    # Regular expression pattern to match CQ codes
    cq_pattern = r'\[CQ:[^\]]+\]'
    # Find all CQ codes in the text
    cq_codes = re.findall(cq_pattern, text)
    # Remove CQ codes from the original text
    clean_text = re.sub(cq_pattern, '', text)
    return cq_codes, clean_text

def send_msg(message, message_type, target_id, ip='192.168.1.104', port='5700'):
    # Prepare the data to send in the request
    data = {
        "message_type": message_type,
        "message": message,
        "auto_escape": "false"
    }
    # Depending on the message type, set the target_id in the data
    if message_type == "private":
        data["user_id"] = target_id
    elif message_type == "group":
        data["group_id"] = target_id
    else:
        return {"error": "Invalid message type"}  
    # Construct the URL
    url = f"http://{ip}:{port}/send_msg"
    try:
        response = requests.get(url, params=data)
        response_data = response.json()
        
        if response.status_code == 200:
            return response_data  # Return the response data
        else:
            return {"error": "Failed to send the message"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def read_prompt(file_path):#读取prompt
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    return prompt
    """
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"
    """
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def check_complete_config(directory):
    role_names = []

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(directory, filename)
            json_file_path = os.path.join(directory, filename.replace(".txt", ".json"))

            # 如果同时存在相应的txt和json文件，则认为配置完整
            if os.path.exists(json_file_path):
                role_name = filename.split(".")[0]
                role_names.append(role_name)

    return role_names

def format_role_list(role_names):
    formatted_list = "支持切换的角色：\n"
    for i, role_name in enumerate(role_names, start=1):
        formatted_list += f"{i}. {role_name}\n"
    return formatted_list.strip()