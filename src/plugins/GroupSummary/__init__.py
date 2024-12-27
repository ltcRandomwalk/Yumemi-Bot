import nonebot
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg
import pytz
from openai import AzureOpenAI
import openai
from openai import OpenAI
import os
from nonebot import require
import nonebot_plugin_session
from nonebot_plugin_session import extract_session, SessionIdType
require("nonebot_plugin_chatrecorder")
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_chatrecorder import get_message_records, get_messages_plain_text
from datetime import datetime, timedelta

from anthropic import Anthropic
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    GROUP,
    Message,
    MessageSegment
)
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="chat",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


chat_event = nonebot.on_command("总结", priority=10, block=True)
system_message = '''
    你是一个消息总结助理。我会发给你一个群聊一天之内的聊天内容，你对聊天记录进行总结。请用“群友”来指代“群内成员”。你的总结应该是一段完整通顺的话，而不是分条列点。如果聊天记录较多，你可以选择一两个有趣话题进行详细总结，但仍应尽量保证总结能涵盖到尽量多的内容。你的总结应该符合聊天记录本身，不要添加聊天记录没有提到的内容。你应该使你的总结显得有趣一些。在你的回复中，只需要回复总结的内容，不要添加其他提示词。
'''

@chat_event.handle()
async def chat_handler(bot: Bot, event: GroupMessageEvent, args: Message=CommandArg()):
    if event.user_id != 295259537:
        await chat_event.finish("测试期间，仅允许bot管理者使用此功能。")
    session = extract_session(bot, event)
    msgs = await get_messages_plain_text(
        session=session,
        id_type=SessionIdType.GROUP,
        types=["message"],
        time_start=datetime.now() - timedelta(days=1),
    )
    msgs = [ msg for msg in msgs if not msg.startswith("#") ]
    reponse = get_response("这是今天的群聊信息，请对它们进行总结:"+"\n".join(msgs))
    await chat_event.finish(f"今日群聊内容总结如下：(By gpt-4o-mini)\n {reponse}")


def get_claude_response(prompt: str):
    try:
        client = Anthropic(
            base_url='https://api.openai-proxy.org/anthropic',
            api_key=os.getenv("CLAUDE_API_KEY"),
        )
        
        message = client.messages.create(
            max_tokens=1024,
            system=system_message,
            messages=[
			    {"role": "user", "content": prompt}
            ],
            model="claude-3-5-haiku-20241022"
        )
        return message.content[0].text
    except Exception as e:
        return repr(e)
    
def get_close_ai_response(prompt: str):
    try:
        client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key=os.getenv("CLAUDE_API_KEY")
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system",  "content": system_message},
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return repr(e)

def get_azure_response(prompt: str):
    try:
        azure_endpoint = os.getenv("OPENAI_ENDPOINT")
        api_key = os.getenv("OPENAI_API_KEY")
        api_version = os.getenv("OPENAI_API_VERSION")
        client = AzureOpenAI(
			azure_endpoint=azure_endpoint,
			api_key=api_key,
			api_version=api_version
		)
        
        deployment_name="gpt-35-turbo"   # Such things can be implemented in Config in the future.
        
        messages = [
			{"role": "system",  "content": system_message},
			{"role": "user", "content": prompt}
		]
        
        response = client.chat.completions.create(
			model=deployment_name,
			messages=messages
		)
        
        return response.choices[0].message.content
    except Exception as e:
        return repr(e)

def get_response(prompt: str):
    return get_close_ai_response(prompt)



async def daily_summary():
    bot = nonebot.get_bot()
    white_list = config.white_list
    for group in white_list:
        msgs = await get_messages_plain_text(
            id2s=[str(group)],
            types=["message"],
            time_start=datetime.now() - timedelta(days=1)
        )
        msgs = [ msg for msg in msgs if not msg.startswith("#") ]
        reponse = get_response("这是今天的群聊信息，请对它们进行总结:"+"\n".join(msgs))
        msg = f"昨日群聊内容总结如下(By gpt-4o-mini)：\n {reponse}"
        await bot.call_api("send_group_msg", group_id=group, message=msg)

scheduler.add_job(daily_summary, "cron", hour=23, minute=55, second=0, id='daily_summary', timezone=pytz.timezone("Asia/Shanghai"))