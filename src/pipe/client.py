import os
import json
from openai import OpenAI
from typing import Dict

BASE_DIR = ".."
CONF_DIR = "config/test_config.json"

class OpenAIClient:
    def __init__(self, config: Dict):
        self.client = OpenAI(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", "https://api.hunyuan.cloud.tencent.com/v1").rstrip('/') + '/',
            timeout=config.get("timeout", 30)
        )
        self.model_name = config.get("model_name", "hunyuan-lite")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        self.top_p = config.get("top_p", 1.0)
        self.presence_penalty = config.get("presence_penalty", 0.0)
        self.frequency_penalty = config.get("frequency_penalty", 0.0)

    def generate(self, prompt: str, **kwargs) -> Dict:
        """执行模型调用，支持动态参数覆盖配置
        
        :param prompt: 输入提示词
        :param kwargs: 可覆盖配置参数（temperature/max_tokens等）
        """
        try:
            params = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
                **kwargs
            }

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **params
            )
            return {
                "content": response.choices[0].message.content,
                "tokens": response.usage.total_tokens if response.usage else 0,
                "model": self.model_name
            }
        except Exception as e:
            return {
                "content": f"API调用失败: {str(e)}",
                "tokens": 0,
                "model": self.model_name
            }

if __name__ == "__main__":
    # 测试配置（优先从json文件读取）
    config_path = os.path.join(BASE_DIR, CONF_DIR)
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)["model_config"]
            print("Reading test config")
    else:
        # 默认测试配置（需替换实际api_key）
        config = {
            "api_key": "your-api-key",
            "base_url": "https://api.example.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1,
            "timeout": 30
        }

    # 初始化客户端
    client = OpenAIClient(config)

    # 测试用例1：基础功能测试
    print("=== 测试1：正常请求 ===")
    response = client.generate("请用一句话介绍华中科技大学")
    print(f"响应内容：{response['content'][:50]}...")  # 显示前50字符
    print(f"消耗tokens：{response['tokens']}")
    print(f"使用模型：{response['model']}\n")

    # 测试用例2：参数覆盖测试
    print("=== 测试2：参数覆盖 ===")
    custom_response = client.generate(
        "列出三个武汉的景点",
        temperature=0.2,
        max_tokens=100
    )
    print(f"短响应内容：{custom_response['content']}\n")

    # 测试用例3：错误处理测试
    print("=== 测试3：错误配置测试 ===")
    error_client = OpenAIClient({"api_key": "invalid_key"})
    error_response = error_client.generate("测试错误")
    print(f"错误响应：{error_response['content']}\n")

    # 测试用例4：边界值测试
    print("=== 测试4：边界值测试 ===")
    edge_response = client.generate(
        "边界测试",
        max_tokens=1
    )
    print(f"单token响应：{edge_response['content']}")