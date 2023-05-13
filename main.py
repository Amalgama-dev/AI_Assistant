import openai
import os
from dotenv import load_dotenv
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from langchain.memory import RedisChatMessageHistory
from pywebio.session import run_js
from langchain.schema import HumanMessage


history = RedisChatMessageHistory("foo", url="redis://redis:6379/0")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

chat_msgs = []



async def main():
    global chat_msgs

    put_markdown("Добро пожаловать в чат!\nАсистент поможет вам в любом вопросе")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)
    nickname = await input("Войти в чат", required=True, placeholder="Ваше имя")

    while True:
        data = await input_group(
            "💭 Новое сообщение",
            [
                input(placeholder="Текст сообщения ...", name="msg"),
                actions(
                    name="cmd",
                    buttons=["Отправить", {"label": "Удалить чат", "type": "cancel"}],
                ),
            ],
            validate=lambda m: ("msg", "Введите текст сообщения!")
            if m["cmd"] == "Отправить" and not m["msg"]
            else None,
        )

        if data is None:
            break

        prompt = data["msg"]
        context = []



        for message in history.messages:
            if type(message) == HumanMessage:
                context.append({"role": "user", "content": message.content})
            else:
                context.append({"role": "assistant", "content": message.content})

        context.append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=context
        )
        messages = completion.choices[0].message["content"]

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data["msg"]))
        history.add_user_message(prompt)
        msg_box.append(put_markdown(f"`Assistant`: {messages}"))
        history.add_ai_message(messages)

    history.clear()
    put_buttons(
        ["Создать новый чат"], onclick=lambda btn: run_js("window.location.reload()")
    )


if __name__ == "__main__":
    start_server(main, debug=True, port=8000, cdn=False)
