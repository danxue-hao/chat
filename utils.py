from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from openai import APITimeoutError

def get_chat_response(prompt, memory: InMemoryChatMessageHistory, openai_api_key):
    # 关键参数 request_timeout=60 延长接口等待时间，解决APITimeoutError
    model = ChatOpenAI(
        model="glm-4-flash",  # 换成轻量快速模型，大幅减少超时概率
        api_key=openai_api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/",
        request_timeout=60  # 全局超时60秒
    )
    chat_prompt = ChatPromptTemplate.from_messages([
        ("placeholder", "{history}"),
        ("human", "{input}")
    ])
    base_chain = chat_prompt | model

    # 修复lambda阻塞问题，标准工厂函数写法
    def get_session_history(session_id: str):
        return memory

    chat_chain = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    try:
        res = chat_chain.invoke({"input": prompt}, config={"session_id": "chat01"})
        return res.content
    except APITimeoutError:
        return "请求超时！原因：网络波动/服务器繁忙，请刷新页面、切换网络或使用glm-4-flash轻量模型重试"