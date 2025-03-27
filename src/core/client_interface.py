from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Dict
from functools import wraps
from typing import Any, Dict

def validate_content(func):
    """装饰器：验证返回的字典是否包含 'content' 键"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Dict[str, Any]:
        response = func(*args, **kwargs)
        if "content" not in response:
            raise ValueError("Response must contain 'content' key")
        if "tokens" not in response:
            raise ValueError("Response must contain 'tokens' key")
        if "model" not in response:
            raise ValueError("Response must contain 'model' key")
        return response
    return wrapper

class IClientMeta(ABCMeta):
    """元类：自动为子类的 response 方法添加装饰器"""
    def __new__(cls, name, bases, namespace, **kwargs):
        # 若子类定义了 response 方法，则自动应用装饰器
        if "response" in namespace and not getattr(namespace["response"], "__isabstractmethod__", False):
            namespace["response"] = validate_content(namespace["response"])
        return super().__new__(cls, name, bases, namespace, **kwargs)

class ILLMClient(metaclass=IClientMeta):
    """
    大模型Client接口
    """    
    @abstractmethod
    def response(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        发送请求并返回响应字典，字典必须包含 'content' 'tokens' 'model' 键

        :param prompt: 请求的提示
        :param kwargs: 其他参数
        :return: 响应的字典
        """
        ...