import aiohttp

async def chat_with_ai(msg_history):
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-ws-H.PHLIIYE.AKpG.MEUCIHwN-veYrNHmZ2apoLGGWjHRVgxygPuZuASSkW82wXYdAiEA67G3MSICyubQ9wvKC-Zigzqdl2PHyysJDt1nfQkRLVg",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-turbo",
        "messages": msg_history
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
