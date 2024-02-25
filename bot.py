from quart import Quart, request, jsonify
import requests
import re
import copy
from utils import *
import os
from gevent import pywsgi
from openai import AsyncOpenAI
import asyncio
import aiohttp
from aiohttp import web

app = Quart(__name__)

@app.route('/', methods=['POST'])
async def handle_post_request():
    global Gzy_bot
    
    data = await request.get_json()
    print(data)
    if data is not None:
        message_id = data.get('message_id')
        user_id = data.get("user_id")
        message_type = data.get('message_type')
        if not message_type:
            return "None", 200
        
        if message_type == 'private':
            target_id = data['user_id']
        elif message_type == 'group':
            target_id = data['group_id']
        else:
            return "None", 200
        
        try:
            cq_codes, message = parse_cq_codes(data['message'])
            # 尝试解析CQ码
        except:
            return 'Error of parsing cq codes', 200
            
        
        if (f'[CQ:at,qq={Gzy_bot.qq}]' not in cq_codes) and message_type != 'private':
            # 如果不是艾特信息，且不是私聊信息
            # 直接返回
            return "None", 200
        else:
            if not Gzy_bot.check_existence(target_id):
                Gzy_bot.register_conversation_manager(target_id, message_type)
                # 如果不存在，就注册一个新对话管理器
        
        
        conversation_manager = Gzy_bot.conversation_map.get(target_id)
        # 取出本次聊天的对话管理器
        
        if message.strip() == 'lock on':
            print(user_id, Gzy_bot.admin)
            if str(user_id) == str(Gzy_bot.admin):
                Gzy_bot.private_lock = True
                await send_msg('上锁成功，现在仅限私聊对话。', message_type, target_id, 
                               ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            else:
                await send_msg(f'大叔~你没有权限喔，只有我的主人 [CQ:at,qq={Gzy_bot.admin}] 有权限~杂鱼~杂鱼❤', 
                               message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            
        elif message.strip() == 'lock off':
            if str(user_id) == str(Gzy_bot.admin):
                Gzy_bot.private_lock = False
                await send_msg('解锁成功，开始提供群聊服务。', message_type, target_id, 
                               ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            else:
                await send_msg(f'大叔~你没有权限喔，只有我的主人 [CQ:at,qq={Gzy_bot.admin}] 有权限~杂鱼~杂鱼❤', 
                               message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            
        elif message.strip() == 'clean' or len(conversation_manager.conversation) > conversation_manager.context_length:
            conversation_manager.conversation = copy.deepcopy(conversation_manager.conversation_init)
            await send_msg('已成功清除上下文！', message_type, target_id, 
                           ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
            return 'Done', 200
        
        elif message.strip() == 'help':
            await send_msg('指令：\n1.clean（清除上下文）\n2.list（用于查看可切换的角色）3.switch（用于切换角色）\n4.lock on 关闭群聊服务 lock off 开启群聊服务\n\n切换角色指令示例：“switch 顾子韵”', \
                     message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
            return 'Done', 200
        
        elif message.strip() == 'list':
            complete_roles = check_complete_config("./prompt")
            formatted_roles = format_role_list(complete_roles)
            await send_msg(formatted_roles, message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
            return 'Done', 200
        
        elif message.strip().split()[0] == 'switch':
            if os.path.exists(f'./prompt/{message.strip().split()[1]}.json') and os.path.exists(
                    f'./prompt/{message.strip().split()[1]}.txt'):
                
                #Prompt设置
                ROLE_CONFIG = load_json(f'./prompt/{message.strip().split()[1]}.json')
                CONVERSATION = ROLE_CONFIG.get("Conversation")
                PROMPT = read_prompt(f'./prompt/{message.strip().split()[1]}.txt').strip()
                CONVERSATION[0]["content"] = PROMPT
                NAMES = ROLE_CONFIG.get("Role")

                # 参数设置
                CONTEXT_LENGTH = int(ROLE_CONFIG.get("Parameters").get("context_length"))#上下文长度
                MAX_TOKENS = int(ROLE_CONFIG.get("Parameters").get("max_tokens"))#最大返回token
                TEMPERATURE = float(ROLE_CONFIG.get("Parameters").get("temperature"))
                TOP_P = float(ROLE_CONFIG.get("Parameters").get("top_p"))
                PRESENCE_PENALTY = float(ROLE_CONFIG.get("Parameters").get("presence_penalty"))
                FREQUENCY_PENALTY = float(ROLE_CONFIG.get("Parameters").get("frequency_penalty"))

                manager = ConversationManager(target_id = target_id, 
                                              type = message_type, 
                                              conversation_init = CONVERSATION, 
                                              conversation = CONVERSATION, 
                                              names = NAMES, 
                                              context_length = CONTEXT_LENGTH, 
                                              max_tokens = MAX_TOKENS, 
                                              temperature = TEMPERATURE, 
                                              top_p = TOP_P, 
                                              presence_penalty = PRESENCE_PENALTY, 
                                              frequency_penalty = FREQUENCY_PENALTY, 
                                              model = Gzy_bot.default.model)
                del Gzy_bot.conversation_map[target_id] 
                Gzy_bot.conversation_map[target_id]= manager
                await send_msg(f"角色切换为【{message.strip().split()[1]}】成功！", message_type,
                               target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            else:
                await send_msg(f"角色【{message.strip().split()[1]}】不存在！", message_type, target_id, 
                               ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
        else:
            if Gzy_bot.private_lock:
                await send_msg(f'大叔，我的主人已经把我关掉了喔！你可以去找我的主人求他解锁喵~ [CQ:at,qq={Gzy_bot.admin}] ', 
                               message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return 'Done', 200
            #await send_msg(f"Hello World!", message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
            conversation_manager.conversation.append({"role": "user", "content": message})
            response = await get_openai_completion(client = Gzy_bot.client,
                                                   messages = conversation_manager.conversation,
                                                   model = conversation_manager.model,
                                                   frequency_penalty = conversation_manager.frequency_penalty,
                                                   presence_penalty = conversation_manager.presence_penalty,
                                                   max_tokens = conversation_manager.max_tokens,
                                                   temperature = conversation_manager.temperature,
                                                   top_p = conversation_manager.top_p)
            if not response:
                return_message = f"Failed to call the OpenAI API".strip()
                await send_msg(return_message, message_type, target_id, ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
                return jsonify(response), 200
            else:
                return_message = f"{response.choices[0].message.content}".strip()
                print("语言模型返回：", return_message)

            conversation_manager.conversation.append({"role": "assistant", "content": return_message})
            print(conversation_manager.conversation)
            if message_type == 'private':
                reply = ''
            else:
                reply = f'[CQ:reply,id={message_id}]'
            await send_msg(reply + return_message, message_type, target_id, 
                           ip=Gzy_bot.shamrock_ip, port=Gzy_bot.shamrock_port)
            
            return 'Done', 200
        
if __name__ == '__main__':
    Gzy_bot = load_config()
    Gzy_bot.print_parameters()
    app.run(host = Gzy_bot.ip, port = Gzy_bot.port)
    #server = pywsgi.WSGIServer((Gzy_bot.ip, Gzy_bot.port), app)
    #server.serve_forever()