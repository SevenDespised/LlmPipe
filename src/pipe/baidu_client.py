import os
import json
import requests
from typing import Dict, Any
from ..core.client_interface import ILLMClient

BASE_DIR = ".."
CONF_DIR = "config/baidu_config.json"

class BaiduClient(ILLMClient):
    def __init__(self, config: Dict = None, config_path: str = None):
        """
        初始化百度文心大模型客户端
        
        :param config: 配置字典，直接提供配置参数
        :param config_path: 配置文件路径，从文件读取配置参数
        """
        # 加载配置
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        else:
            self.config = config or {}
            
        # 设置基础参数
        self.api_key = self.config.get("api_key", "")
        self.secret_key = self.config.get("secret_key", "")
        self.model = self.config.get("model", "ernie-lite-8k")
        
        # 设置API请求参数
        self.temperature = self.config.get("temperature", 0.95)
        self.top_p = self.config.get("top_p", 0.7)
        self.penalty_score = self.config.get("penalty_score", 1.0)
        
        # 设置URL配置
        self.urls = self.config.get("urls", {})
        self.token_url = self.urls.get("token_url", "https://aip.baidubce.com/oauth/2.0/token")
        self.api_base_url = self.urls.get("api_base_url", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat")
        
        # 初始访问令牌为空
        self.access_token = None
    
    def get_access_token(self) -> str:
        """
        获取百度API访问令牌
        
        :return: access_token字符串
        """
        # 使用配置中的token_url
        params = {
            "grant_type": "client_credentials", 
            "client_id": self.api_key, 
            "client_secret": self.secret_key
        }
        response = requests.post(self.token_url, params=params)
        result = response.json()
        
        # 错误处理
        if "access_token" not in result:
            error_msg = f"获取访问令牌失败: {result}"
            raise ValueError(error_msg)
            
        return result.get("access_token")
    
    def response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        发送请求至百度文心API并返回响应
        
        :param prompt: 用户输入的提示
        :param kwargs: 其他参数，可覆盖默认配置
        :return: 包含content、tokens和model的响应字典
        """
        try:
            # 确保有有效的访问令牌
            if not self.access_token:
                self.access_token = self.get_access_token()
            
            # 准备API URL和模型名称
            model = kwargs.get("model", self.model)
            # 使用配置中的api_base_url
            url = f"{self.api_base_url}/{model}?access_token={self.access_token}"
            
            # 准备请求消息
            messages = []
            # 处理历史消息，如果有的话
            if "history" in kwargs and kwargs["history"]:
                messages.extend(kwargs["history"])
            # 添加当前提示
            messages.append({"role": "user", "content": prompt})
            
            # 准备请求参数
            payload = {
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p),
                "penalty_score": kwargs.get("penalty_score", self.penalty_score)
            }
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
            )
            result = response.json()
            
            # 处理可能的错误
            if "error_code" in result:
                # 如果是token过期，尝试刷新token后重试
                if result.get("error_code") in [110, 111]:  # token过期的错误代码
                    self.access_token = self.get_access_token()
                    return self.response(prompt, **kwargs)
                
                error_msg = f"API调用错误: {result}"
                return {
                    "content": error_msg,
                    "tokens": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    },
                    "model": model
                }
            
            # 构造返回结果
            return {
                "content": result.get("result", ""),
                "tokens": {
                    "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": result.get("usage", {}).get("total_tokens", 0)
                },
                "model": model
            }
            
        except Exception as e:
            return {
                "content": f"API请求发生异常: {str(e)}",
                "tokens": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "model": model if 'model' in locals() else self.model
            }


if __name__ == "__main__":
    # 测试配置（优先从json文件读取）
    config_path = os.path.join(BASE_DIR, CONF_DIR)
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            print("Reading baidu config from file")
    else:
        # 默认测试配置（需替换实际api_key和secret_key）
        config = {
            "api_key": "your-api-key",
            "secret_key": "your-secret-key",
            "model": "ernie-lite-8k",
            "temperature": 0.95,
            "top_p": 0.7,
            "penalty_score": 1.0,
            "urls": {
                "token_url": "https://aip.baidubce.com/oauth/2.0/token",
                "api_base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat"
            }
        }

    # 初始化客户端
    client = BaiduClient(config)

    # 测试用例1：基础功能测试
    print("=== 测试1：正常请求 ===")
    response = client.response("请用一句话介绍华中科技大学")
    print(f"响应内容：{response['content'][:50]}...")  # 显示前50字符
    print(f"消耗tokens：{response['tokens']}")
    print(f"使用模型：{response['model']}\n")

    # 测试用例2：参数覆盖测试
    print("=== 测试2：参数覆盖 ===")
    custom_response = client.response(
        "列出三个武汉的景点",
        temperature=0.2,
        top_p=0.9
    )
    print(f"自定义参数响应：{custom_response['content']}\n")

    # 测试用例3：错误处理测试
    print("=== 测试3：错误配置测试 ===")
    error_client = BaiduClient({"api_key": "invalid_key", "secret_key": "invalid_secret"})
    error_response = error_client.response("测试错误")
    print(f"错误响应：{error_response['content']}\n")
