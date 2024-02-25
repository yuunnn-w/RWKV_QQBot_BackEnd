import configparser
import requests
import re
import json
import os
import openai
import httpx
import asyncio
from openai import AsyncOpenAI
import copy

def read_config(Section, key, file_path = './config.ini'):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')

    # 检查指定的 section 和 key 是否存在于配置文件中
    if config.has_section(Section) and config.has_option(Section, key):
        value = config.get(Section, key)
        return value
    else:
        return None
    
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

async def get_openai_completion(client, messages, model="gpt-3.5-turbo",
                                frequency_penalty=None, presence_penalty=None,
                                max_tokens=None, temperature=None, top_p=None,
                                timeout=None):
    try:
        chat_completion = await client.chat.completions.create(
            messages=messages,
            model=model,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        return chat_completion
    except Exception as e:
        print(f"Error: {e}")
        return None

def update_token_count(file_name, token_count):
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

def parse_cq_codes(text):
    # Regular expression pattern to match CQ codes
    cq_pattern = r'\[CQ:[^\]]+\]'
    
    # Find all CQ codes in the text
    cq_codes = re.findall(cq_pattern, text)
    
    # Remove CQ codes from the original text
    clean_text = re.sub(cq_pattern, '', text)
    
    return cq_codes, clean_text

async def send_msg(message, message_type, target_id, ip='192.168.1.104', port='5700', if_CQ='false'):
    # Prepare the data to send in the request
    data = {
        "message_type": message_type,
        "message": message,
        "auto_escape": if_CQ  # 是否解析CQ码
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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=data)
            response_data = response.json()
            
            if response.status_code == 200:
                return response_data  # Return the response data
            else:
                return {"error": "Failed to send the message"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

def read_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt = file.read()
    return prompt
    """
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"
    """

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


class ConversationManager:
    def __init__(self, target_id: str, type: str, conversation_init: list, conversation: list, names: list, context_length: int, max_tokens: int, temperature: float, top_p: float, presence_penalty: float, frequency_penalty: float, model: str):
        self.target_id = target_id
        self.type = type
        self.conversation_init = copy.deepcopy(conversation_init)
        self.conversation = copy.deepcopy(conversation)
        self.names = copy.deepcopy(names)
        self.context_length = context_length
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.model = model
        
    def print_parameters(self):
        print("目标ID:", self.target_id)
        print("目标类型:", self.type)
        print("初始化对话:", self.conversation_init)
        print("角色名称:", self.names)
        print("上下文长度（即最大对话轮数）:", self.context_length)
        print("最大token数:", self.max_tokens)
        print("温度:", self.temperature)
        print("Top P:", self.top_p)
        print("主题重复度惩罚因子:", self.presence_penalty)
        print("重复度惩罚因子:", self.frequency_penalty)
        print("模型:", self.model)
        
class Bot:
    def __init__(self, default: ConversationManager, server_ip: str, server_port: int, shamrock_ip: str, shamrock_port: int, QQ: str, Admin_QQ: str, client: AsyncOpenAI, token_count: str):
        self.default = default
        self.conversation_map = {}
        self.private_lock = False
        self.ip = server_ip
        self.port = server_port
        self.shamrock_ip = shamrock_ip
        self.shamrock_port = shamrock_port
        self.qq = QQ
        self.admin = Admin_QQ
        self.client = client
        self.token_count = token_count
        
    def print_parameters(self):
        print("默认对话管理器参数:\n")
        self.default.print_parameters()
        print("\n")
        print("服务器IP:", self.ip)
        print("服务器端口:", self.port)
        print("Shamrock_IP:", self.shamrock_ip)
        print("Shamrock端口:", self.shamrock_port)
        print("QQ号:", self.qq)
        print("Token计数文件:", self.token_count)
        
    def register_conversation_manager(self, target_id: str, type: str):
        # 从self.default中获取其他参数
        conversation_init = copy.deepcopy(self.default.conversation_init)
        conversation = copy.deepcopy(self.default.conversation)
        names = copy.deepcopy(self.default.names)
        context_length = self.default.context_length
        max_tokens = self.default.max_tokens
        temperature = self.default.temperature
        top_p = self.default.top_p
        presence_penalty = self.default.presence_penalty
        frequency_penalty = self.default.frequency_penalty
        model = self.default.model
        
        # 创建新的ConversationManager对象并添加到self.conversation_map中
        new_conversation_manager = ConversationManager(target_id=target_id, type=type, 
                                                       conversation_init=conversation_init, 
                                                       conversation=conversation, 
                                                       names=names, 
                                                       context_length=context_length, 
                                                       max_tokens=max_tokens, 
                                                       temperature=temperature, 
                                                       top_p=top_p, 
                                                       presence_penalty=presence_penalty, 
                                                       frequency_penalty=frequency_penalty, 
                                                       model=model)
        self.conversation_map[target_id] = new_conversation_manager

    def get_conversation_manager(self, target_id: str) -> ConversationManager:
        return self.conversation_map.get(target_id, self.default)

    def check_existence(self, target_id: str):
        if target_id in self.conversation_map:
            return True
        else:
            return False

    def delete_conversation_manager(self, target_id: str) -> bool:
        if target_id in self.conversation_map:
            del self.conversation_map[target_id]
            return True
        else:
            return False
        
def load_config():
    #服务器设置
    SERVER_IP = read_config("Server", "IP")
    SERVER_PORT = int(read_config("Server", "PORT"))

    MODEL = str(read_config("Model", "MODEL"))

    #Prompt设置
    ROLE_CONFIG = load_json(read_config("Prompt", "ROLE_CONFIG"))
    CONVERSATION = ROLE_CONFIG.get("Conversation")
    PROMPT = read_prompt(read_config("Prompt", "ROLE_PROMPT")).strip()
    CONVERSATION[0]["content"] = PROMPT
    NAMES = ROLE_CONFIG.get("Role")

    # 参数设置
    CONTEXT_LENGTH = int(ROLE_CONFIG.get("Parameters").get("context_length"))#上下文长度
    MAX_TOKENS = int(ROLE_CONFIG.get("Parameters").get("max_tokens"))#最大返回token
    TEMPERATURE = float(ROLE_CONFIG.get("Parameters").get("temperature"))
    TOP_P = float(ROLE_CONFIG.get("Parameters").get("top_p"))
    PRESENCE_PENALTY = float(ROLE_CONFIG.get("Parameters").get("presence_penalty"))
    FREQUENCY_PENALTY = float(ROLE_CONFIG.get("Parameters").get("frequency_penalty"))

    #OpenAI接口设置
    URL = str(read_config("OpenAI", "URL"))
    API_KEY = str(read_config("OpenAI", "API_KEY"))
    TOKEN_COUNT = read_config("OpenAI", "TOKEN_COUNT")
    Client = AsyncOpenAI(api_key=API_KEY, base_url=URL)

    #Shamrock框架交互设置
    SHAMROCK_IP = str(read_config("Shamrock", "IP"))
    SHAMROCK_PORT = read_config("Shamrock", "PORT")
    QQ = str(read_config("Shamrock", "QQ")) #这里需要你在配置文件中改成你挂shamrock的QQ号
    Admin_QQ = str(read_config("Shamrock", "Admin_QQ")) # 管理员QQ

    default_manager = ConversationManager(target_id = "114514", 
                                          type = "default", 
                                          conversation_init = CONVERSATION, 
                                          conversation = CONVERSATION, 
                                          names = NAMES, 
                                          context_length = CONTEXT_LENGTH, 
                                          max_tokens = MAX_TOKENS, 
                                          temperature = TEMPERATURE, 
                                          top_p = TOP_P, 
                                          presence_penalty = PRESENCE_PENALTY, 
                                          frequency_penalty = FREQUENCY_PENALTY, 
                                          model = MODEL)
    bot = Bot(default = default_manager,
              server_ip = SERVER_IP,
              server_port = SERVER_PORT,
              shamrock_ip = SHAMROCK_IP,
              shamrock_port = SHAMROCK_PORT,
              QQ = QQ,
              Admin_QQ = Admin_QQ,
              client = Client,
              token_count = TOKEN_COUNT)
    return bot
