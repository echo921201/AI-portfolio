# -*- coding: utf-8 -*-
# W6: 双引擎封装 —— 本地 Ollama + 云端 DeepSeek
# 用法：from llm import LLM
#       LLM().ask("问题", prefer="local")  本地优先
#       LLM().ask("问题", prefer="api")    云端优先

import os
import requests
import openai


def _load_dotenv(path=".env"):
    # 读取本目录 .env 里的密钥（.env 不进 git 仓库）
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
    def __init__(self, model=None):
        self.model = model or os.getenv("LOCAL_MODEL", "qwen2.5:0.5b")

    def ask(self, prompt, temperature=0.7, max_tokens=800):
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
        r.raise_for_status()
        return r.json()["message"]["content"]


class APIEngine:
    def __init__(self):
        self.client = None

    def _ensure_client(self):
        if self.client is None:
            self.client = openai.OpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
            )

    def ask(self, prompt, temperature=0.7, max_tokens=800):
        self._ensure_client()
        r = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return r.choices[0].message.content


class LLM:
    def __init__(self, local_model=None):
        self.local = LocalEngine(local_model)
        self.api = APIEngine()

    def ask(self, prompt, prefer="local", **kw):
        if prefer == "local":
            first, second = self.local, self.api
        else:
            first, second = self.api, self.local
        try:
            return first.ask(prompt, **kw)
        except Exception as e:
            print("[首选引擎失败，自动切换] %s" % e)
            return second.ask(prompt, **kw)


if __name__ == "__main__":
    q = "给《愚公移山》出一道 HSK4 阅读题"
    print(LLM().ask(q, prefer="local"))
