from prompt_optimization.utils.read_prompt import read_prompt
from prompt_optimization.utils.example_sample import sampled_example_str
from prompt_optimization.utils.read_template import read_template

class PromptOptimizer:
    """
    PromptOptimizer 类用于优化和生成指令提示信息。它通过添加各种类型的提示信息来构建一个完整的提示字符串。

    核心功能包括：
    - 添加指令提示信息
    - 添加上下文提示信息
    - 添加输入提示信息
    - 添加输出提示信息
    - 添加输出格式提示信息
    - 添加输出约束提示信息
    - 添加聊天系统提示信息
    - 添加聊天格式提示信息
    - 添加聊天历史记录
    - 添加示例数据

    使用示例：
    optimizer = PromptOptimizer("示例提示", language="en")
    optimizer.add_instruction("指令").add_context("上下文").get_optimized_prompt()
    """

    def __init__(self, prompt, language="zh"):
        """
        初始化 PromptOptimizer 对象。

        参数：
        - prompt (str): 初始的提示信息。
        - language (str, optional): 提示信息的语言，默认为 "zh"。
        """
        self.prompt = prompt
        self.language = language
        self.optimized_prompt = ""

    # 添加指令提示信息
    def add_instruction(self, instruction):
        instruction_prompt = read_prompt("instruction", self.language, content=instruction)
        self.optimized_prompt += instruction_prompt
        return self

    # 添加上下文提示信息
    def add_context(self, context):
        context_prompt = read_prompt("context", self.language, content=context)
        self.optimized_prompt += context_prompt
        return self

    # 在输入前增加"输入："
    def add_input_text(self, input_text="输入"):
        input_prompt = read_prompt("input", self.language, input_text=input_text, prompt=self.prompt)
        self.optimized_prompt += input_prompt
        return self
    
    # 在输出前增加"输出："
    def add_output_text(self, output_text="输出"):
        output_prompt = read_prompt("output", self.language, output_text=output_text)
        self.optimized_prompt += output_prompt
        return self

    # 添加输出格式提示信息
    def add_output_format(self, output_format):
        output_format_prompt = read_prompt("output_format", self.language, content=output_format)
        self.optimized_prompt += output_format_prompt
        return self

    # 添加输出约束提示信息
    def add_output_constraint(self, constraint):
        constraint_prompt = read_prompt("output_constraint", self.language, content=constraint)
        self.optimized_prompt += constraint_prompt
        return self

    # 增加基本格式，统一调用上述方法
    def add_basic_format(self, instruction, context, output_format, constraint):
        self.add_instruction(instruction).add_context(context).add_input_text().add_output_format(
            output_format).add_output_constraint(constraint).add_output_text()
        return self

    # 添加聊天系统提示信息
    def add_chat_system(self, system_content=" "):
        system_prompt = read_prompt("chat_system", self.language, content=system_content)
        self.optimized_prompt += system_prompt
        return self

    # 添加聊天格式提示信息
    def add_chat_format(self, your_name="用户", your_message=None, assistant_name="助手", assistant_message=""):
        if your_message is None:
            your_message = self.prompt
        chat_format_prompt = read_prompt("chat_format", self.language,
                                         your_name=your_name,
                                         your_message=your_message,
                                         assistant_name=assistant_name,
                                         assistant_message=assistant_message)
        self.optimized_prompt += chat_format_prompt
        return self
    # 添加聊天历史记录
    def add_chat_history(self, history_message: list, your_name="用户", assistant_name="助手"):
        for message in history_message:
            if isinstance(message, list):
                if len(message) == 2:
                    self.add_chat_format(your_name=your_name,
                                         your_message=message[0],
                                         assistant_name=assistant_name,
                                         assistant_message=message[1])
                else:
                    raise ValueError("history_message list must have two elements")
            elif isinstance(message, str):
                self.optimized_prompt += message + "\n"
        return self
    # 添加带历史纪录的聊天格式，统一调用上述方法。
    def add_chat_format_with_history(self, history_message = [], system_content=" ", your_name="用户", assistant_name="助手"):
        self.add_chat_system(system_content).add_chat_history(history_message, your_name, assistant_name).add_chat_format(your_name=your_name, assistant_name=assistant_name)
        return self
    # 添加采样示例
    def add_example(self, dataset: list, x_key: str, y_key: str, sample_size=3, sampling_method='random'):
        self.optimized_prompt += sampled_example_str(dataset, x_key, y_key, sample_size, sampling_method)
        return self
    # 添加模板, to_who决定向模板中添加的是原始prompt还是优化后的prompt
    def add_template(self, template_path: str, prompt_key: str, to_who: str = "optimized_prompt", **kwargs):
        if prompt_key not in kwargs:
            raise ValueError("prompt_key must be in kwargs")
        if prompt_key != "":
            kwargs[prompt_key] = self.optimized_prompt if to_who == "optimized_prompt" and self.optimized_prompt != "" else self.prompt
        self.optimized_prompt = read_template(template_path, **kwargs)
        return self 
    def get_optimized_prompt(self):
        return self.optimized_prompt

# 示例用例

# 示例 1: 添加基本格式提示信息
original_prompt = "请分析这段文本的情感倾向"
optimizer = PromptOptimizer(original_prompt)
instruction = "仔细分析文本中的情感词汇和语气"
context = "该文本来自一篇产品评论"
output_format = "以积极、消极或中性进行回复"
constraint = "回复需简洁明了"

optimizer.add_basic_format(instruction, context, output_format, constraint)
optimized_prompt_1 = optimizer.get_optimized_prompt()
print("示例 1: 添加基本格式提示信息")
print(optimized_prompt_1)
print("-" * 50)

# 示例 2: 添加聊天相关提示信息
original_prompt = "今天天气怎么样？"
optimizer = PromptOptimizer(original_prompt)
system_content = "这是一个天气咨询的聊天场景"
history_message = [["昨天天气很好", "是的，阳光明媚"], ["那今天呢", "还不清楚，我去查一下"]]

optimizer.add_chat_format_with_history(history_message, system_content)
optimized_prompt_2 = optimizer.get_optimized_prompt()
print("示例 2: 添加聊天相关提示信息")
print(optimized_prompt_2)