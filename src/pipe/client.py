import os
import json
import requests
from typing import Any, Dict
from openai import OpenAI
from typing import Dict
from ..core.client_interface import ILLMClient

BASE_DIR = ".."
CONF_DIR = "config/test_config.json"

class OpenAIClient(ILLMClient):
    def __init__(self, config: Dict):
        # 必选参数验证
        if "api_key" not in config:
            raise ValueError("必须提供api_key")
        if "base_url" not in config:
            raise ValueError("必须提供base_url")
        if "model_name" not in config:
            raise ValueError("必须提供model_name")
        
        # 提取客户端初始化需要的特殊参数
        client_params = {
            "api_key": config["api_key"],
            "base_url": config["base_url"].rstrip('/') + '/'
        }
        if "timeout" in config:
            client_params["timeout"] = config["timeout"]
            
        # 初始化OpenAI客户端
        self.client = OpenAI(**client_params)
        
        # 提取model_name参数
        self.model_name = config["model_name"]
        
        # 存储所有其他参数为模型配置 - 不再预定义列表
        self.model_config = {k: v for k, v in config.items() 
                           if k not in ["api_key", "base_url", "timeout", "model_name"]}
    
    def response(self, prompt: str, **kwargs) -> Dict:
        """执行模型调用，支持动态参数覆盖配置
        
        :param prompt: 输入提示词
        :param kwargs: 可覆盖配置参数（temperature/max_tokens等）
        """
        try:
            params = {**self.model_config, **kwargs}
            
            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.model_name),
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

class BaiduClient(ILLMClient):
    def __init__(self, config: Dict):
        # 必选参数验证
        if "api_key" not in self.config:
            raise ValueError("必须提供api_key")
        if "secret_key" not in self.config:
            raise ValueError("必须提供secret_key")
        if "model" not in self.config:
            raise ValueError("必须提供model")
        # 加载配置
        self.config = config
            
        # 提取基础参数
        self.api_key = self.config["api_key"]
        self.secret_key = self.config["secret_key"]
        self.model_name = self.config.get("model", "ernie-lite-8k")
        
        # 提取URL配置
        self.urls = self.config.get("urls", {})
        if "token_url" not in self.urls:
            raise ValueError("必须提供token_url")
        if "api_base_url" not in self.urls:
            raise ValueError("必须提供api_base_url")
        self.token_url = self.urls["token_url"]
        self.api_base_url = self.urls.get["api_base_url"]
        
        # 存储所有其他参数为模型配置
        self.model_config = {k: v for k, v in self.config.items() 
                           if k not in ["api_key", "secret_key", "model", "urls"]}
        
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
            # 合并配置参数和动态参数
            params = {**self.model_config, **kwargs}
            
            # 确保有有效的访问令牌
            if not self.access_token:
                self.access_token = self.get_access_token()
            
            # 准备API URL和模型名称
            model = params.get("model", self.model_name)
            # 使用配置中的api_base_url
            url = f"{self.api_base_url}/{model}?access_token={self.access_token}"
            
            # 准备请求消息
            messages = []
            # 处理历史消息，如果有的话
            if "history" in params and params["history"]:
                messages.extend(params["history"])
            # 添加当前提示
            messages.append({"role": "user", "content": prompt})
            
            # 准备请求参数
            payload = {
                "messages": messages,
                "temperature": params.get("temperature", 0.95),
                "top_p": params.get("top_p", 0.7),
                "penalty_score": params.get("penalty_score", 1.0)
            }
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
            )
            result = response.json()
            
            # 构造返回结果
            return {
                "content": result.get("result", ""),
                "tokens": response.usage.total_tokens if response.usage else 0,
                "model": self.model_name
            }
            
        except Exception as e:
            return {
                "content": f"API调用失败: {str(e)}",
                "tokens": 0,
                "model": self.model_name
            }