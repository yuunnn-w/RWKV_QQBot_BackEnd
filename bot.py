from flask import Flask, request, jsonify
import requests
import re
import copy
from utils import *
import os
from gevent import pywsgi

app = Flask(__name__)

#服务器设置
SERVER_IP = read_config("Server", "IP")
SERVER_PORT = int(read_config("Server", "PORT"))

#Prompt设置
ROLE_CONFIG = load_json(read_config("Prompt", "ROLE_CONFIG"))
CONSERVATION = ROLE_CONFIG.get('Conservation')
PROMPT = read_prompt(read_config("Prompt", "ROLE_PROMPT")).strip()
CONSERVATION[0]["content"] = PROMPT
NAMES = ROLE_CONFIG.get("Role")
CONTEXT_LENGTH = int(read_config("Prompt", "CONTEXT_LENGTH"))#上下文长度

#OpenAI接口设置
URL = read_config("OpenAI", "URL")
API_KEY = read_config("OpenAI", "API_KEY")
TOKEN_COUNT = read_config("OpenAI", "TOKEN_COUNT")

#Shamrock框架交互设置
SHAMROCK_IP = read_config("Shamrock", "IP")
SHAMROCK_PORT = read_config("Shamrock", "PORT")
QQ = read_config("Shamrock", "QQ") #这里需要你在配置文件中改成你挂shamrock的QQ号

#Model模型设置
MAX_TOKENS = int(read_config("Model", "MAX_TOKENS"))
TEMPERATURE = float(read_config("Model", "TEMPERATURE"))
TOP_P = float(read_config("Model", "TOP_P"))
PRESENCE_PENALTY = float(read_config("Model", "PRESENCE_PENALTY"))
FREQUENCY_PENALTY = float(read_config("Model", "FREQUENCY_PENALTY"))
PENALTY_DECAY = float(read_config("Model", "PENALTY_DECAY"))
MODEL = read_config("Model", "MODEL")

Private_Lock = False #全局私聊锁
conversation = copy.deepcopy(CONSERVATION)

@app.route('/', methods=['POST'])
def handle_post_request():
    global Private_Lock
    global conversation
    global CONSERVATION
    global NAMES
    
    data = request.get_json()
    #print(data)
    if data is not None:
        try:
            cq_codes, message = parse_cq_codes(data['message'])
        except:
            return 'OK', 200
        
        message_id = data['message_id']
        message_type = data['message_type']
        
        if message_type == 'private':
            target_id = data['user_id']
            if message.strip() == 'lock on':#如果接收到lock on的私聊消息，就开启私聊锁，此时只能进行私聊对话
                Private_Lock = True
                send_msg('LOCK ON', message_type, target_id)
                return 'OK', 200
            elif message.strip() == 'lock off':#关闭私聊锁
                Private_Lock = False
                send_msg('LOCK OFF', message_type, target_id)
                return 'OK', 200
            
        elif message_type == 'group':
            if (f'[CQ:at,qq={QQ}]' not in cq_codes) or Private_Lock:
                if Private_Lock and f'[CQ:at,qq={QQ}]' in cq_codes:
                    send_msg('很抱歉，管理员已暂停本AI服务，请联系管理员解除锁定。', message_type, data['group_id'])
                return 'Pause Service!', 200
            else:
                target_id = data['group_id']
                
        if message.strip() == 'clean' or len(conversation) > CONTEXT_LENGTH:
            conversation = copy.deepcopy(CONSERVATION)
            send_msg('已成功清除上下文！', message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
            return 'Done', 200
            
        elif message.strip() == 'help':
            send_msg('指令：\n1.clean（清除上下文）\n2.list（用于查看可切换的角色）3.switch（用于切换角色）\n\n切换角色指令示例：“switch 顾子韵”',\
                     message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
            return 'Done', 200
        
        elif message.strip().split()[0] == 'switch':
            if os.path.exists(f'./prompt/{message.strip().split()[1]}.json') and os.path.exists(f'./prompt/{message.strip().split()[1]}.txt'):
                ROLE_CONFIG = load_json(f'./prompt/{message.strip().split()[1]}.json')
                CONSERVATION = ROLE_CONFIG.get('Conservation')
                PROMPT = read_prompt(f'./prompt/{message.strip().split()[1]}.txt').strip()
                CONSERVATION[0]["content"] = PROMPT
                NAMES = ROLE_CONFIG.get("Role")
                conversation = copy.deepcopy(CONSERVATION)
                send_msg(f"角色切换为【{message.strip().split()[1]}】成功！", message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
                return 'Done', 200
            else:
                send_msg(f"角色【{message.strip().split()[1]}】不存在！", message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
                return 'Done', 200
            
        elif message.strip() == 'list':
            complete_roles = check_complete_config("./prompt")
            formatted_roles = format_role_list(complete_roles)
            send_msg(formatted_roles, message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
            return 'Done', 200
        
        else:
            conversation.append({"role": "user", "content": message})
            #如果需要对接OpenAI api接口，需要删除一些参数，需要删掉"stop"和"penalty_decay"以及"names"
            #"stop"、"penalty_decay"、"names"这三个参数是ai00 rwkv server特有的
            payload = {
                "messages": conversation,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "presence_penalty": PRESENCE_PENALTY,
                "frequency_penalty": FREQUENCY_PENALTY,
                "penalty_decay": PENALTY_DECAY,
                "stop": ["\n\n","\nUser:","User:"],
                "stream": False,
                "model": MODEL,
                "names": NAMES, #该参数用于映射对话人物姓名，加深催眠效果
                #"logit_bias":{261:-1}
            }
            #print(payload)
            """
            proxy_dict = {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890",
            }
            """
            #暂时废弃掉的代理
            response = call_openai_api(payload, URL, API_KEY)#, proxy_dict)
            if "error" in response:
                return_message = f"Error: {response['error']}".strip()
                print(f"Error: {response['error']}")
                send_msg(return_message, message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
                return jsonify(response), 200
            else:
                return_message = f"{response['choices'][0]['message']['content']}".strip()
                print("RWKV5:", return_message) #打印模型返回信息
                token_usage = int(response.get('usage').get('total_tokens')) #这里计算消耗的token数目
                update_token_count(file_name = TOKEN_COUNT, token_count = token_usage)
                #计算token

            # Append the assistant's response to the conversation
            conversation.append({"role": "assistant", "content": return_message})
            if message_type == 'private':#回复私聊不需要reply
                reply = ''
            else:
                reply = f'[CQ:reply,id={message_id}]'
            response = send_msg(reply+return_message, message_type, target_id, ip=SHAMROCK_IP, port=SHAMROCK_PORT)
            #向Shamrock发送消息
            return "Successfully Send!", 200
    else:
        return "Invalid JSON data received", 400  # Return a 400 Bad Request response if the data is not valid JSON

if __name__ == '__main__':
    #app.run(host = SERVER_IP, port = SERVER_PORT)
    server = pywsgi.WSGIServer((SERVER_IP, SERVER_PORT), app)
    server.serve_forever()