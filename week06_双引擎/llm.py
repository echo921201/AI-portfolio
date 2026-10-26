# -*- coding: utf-8 -*-
# W6: 双引擎封装 —— 本地 Ollama + 云端 DeepSeek，统一接口
# 调用方式：from llm import LLM
#           LLM().ask("你的问题", prefer="local")   # 本地优先
#           LLM().ask("你的问题", prefer="api")     # 云端优先

import os
import requests
import openai


def _load_dotenv(path=".env"):
    # 轻量读取本目录的 .env，把密钥等变量写进环境变量（.env 不进 git 仓库）
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


_load_dotenv()


class LocalEngine:
    """本地引擎：Ollama http 直连（隐私优先、断网可用）"""

    def __init__(self, model=None):
        # 模型名不写死，可用环境变量 LOCAL_MODEL 覆盖，默认 qwen2.5:0.5b
        self.model = model or os.getenv("LOCAL_MODEL", "qwen2.5:0.5b")

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        # timeout=60 必须留：本地首次装载可能要 30 秒左右，不设超时会永久卡住
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=60,
        )
        # 模型名打错会返回 404，让它当场报错而不是返回空答案
        r.raise_for_status()
        return r.json()["message"]["content"]


class APIEngine:
    """云端引擎：DeepSeek（复杂任务、本地失败兜底）"""

    def __init__(self):
        self.client = None  # 先不建客户端！按需创建

    def _ensure_client(self):
        # 第一次真调用时才创建客户端，避免没配密钥就连纯本地模式都进不去
        if self.client is None:
            self.client = openai.OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
            )

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        self._ensure_client()  # 第一次真调用才建
        r = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content


class LLM:
    """统一入口：持有两个引擎，负责 prefer 切换与双向异常回退"""

    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def ask(self, prompt, prefer="local", **kw):
        # 按 prefer 决定首选/备用引擎：local 则本地优先，api 则云端优先
        if prefer == "local":
            first, second = self.local, self.api
        else:
            first, second = self.api, self.local
        try:
            return first.ask(prompt, **kw)
        except Exception as e:
            # 不吞异常：打印切换原因，这行日志就是你的测试证据
            print("[首选引擎失败，自动切换] %s" % e)
            return second.ask(prompt, **kw)


if __name__ == "__main__":
    # 直接运行本文件可做一次快速自检
    q = "给《愚公移山》出一道 HSK4 阅读题"
    print("===== 本地优先 =====")
    print(LLM().ask(q, prefer="local"))
