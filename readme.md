# LLMPipe

## 简介
该模块实现了一个提示工程算法的流水线处理程序，通过动态加载自定义的流水线组件，依次执行各个组件的提示词生成逻辑，并调用大语言模型（LLM）进行交互，最终输出处理结果。主要目的是提供一个灵活的框架，方便用户根据自己的需求定制和扩展提示词生成流程。

## 功能介绍
### 动态加载模块
- 使用 `importlib` 库动态加载自定义的流水线组件
- 动态加载模型客户端，支持不同的模型配置。

### 流水线执行
- 按照配置文件中定义的处理链顺序，依次执行各个提示词组件。
- 每个组件接收初始输入或上一组件经大模型处理后的响应输出，并生成相应的提示词。
- 调用大语言模型生成响应，并对响应进行解析。
- 记录每个处理阶段的详细信息，包括提示词、原始响应、解析后的输出、状态和使用的令牌数。

### 执行流程示例
（其中，小写单词代表输入或输出，大写单词代表功能组件）：<br>
input -> COMPONENT1 -> prompt1 -> LLM -> response1 ->
COMPONENT2 -> prompt2 -> LLM -> response2 -> POSTPROCESS -> output

## 使用说明
### 配置文件
你可以自定义配置文件，或直接在代码中硬编码，数据结构示例内容如下：
```json
{
  "processing_chain": [
      {
          "name": "test_function1",
          "module": "components.test1",
          "init_kwargs": {"system": "you are a pirate"}
      },
      {
          "name": "test_function2",
          "module": "components.test2"
      }
  ],
  "model_config": {
      "api_key": "your-api-key",
      "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
      "model_name": "hunyuan-lite",
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 0.9,
      "presence_penalty": 0.1,
      "frequency_penalty": 0.1,
      "timeout": 30
  },
  "stage_output": [
      "test_function1"
  ],
  "max_history_length": 0
}
```
其中，"processing_chain"键为自定义的流水线组件相关配置，"model_config"键为open-ai大模型接口相关参数。

### processing_chain配置说明
- name(str): 组件名称
- module(str): importlib导入组件路径
- init_kwargs(Dict): （可选）组件初始化参数<br>
根据设置的module的内容，建立组件文件夹，并在文件夹中分别编写每个组件的代码文件。
> 例如，如果你的文件夹结构为/components/test1.py，module的内容应该设置为"components.test1"

### component编写说明
组件间数据交互的方式是自定义的，这取决于你如何对llm进行提示工程。**推荐约束大模型返回json格式，流水线将自动帮你解析为字典**，否则会直接传递原始响应。<br>
流水线组件代码至少应实现**Processor类**<br>
Processor类至少应实现：<br>
- **__init__方法**：用于类的初始构造<br>
输入：自选（需要相应更改config）<br>
输出：无
- **generate方法**：用于提示词生成<br>
输入：input_data(**必须**)、stage_output: List<Dict>(**必须，但可以不使用**)<br>
1.input_data为上一组件的输出或初始输入<br>
2.stage_output所有阶段输出的列表，由pipeline定义，其中也包括原始输入。<br>
输出：大模型提示词，用于输入open-ai-client<br>

### model_config配置说明
代码直接调用open-ai新版SDK，model_config参数说明详见[open-ai相关文档](https://www.openaidoc.com.cn/)

## 依赖
代码使用python3.12.9编写，所有库均使用pip直接安装，无需特殊指定版本。理论来说应该兼容大多数python3。需要注意的是旧版openai的SDK可能有不同的调用方法。<br>
命令行内运行：<br>
`pip install typing importlib openai`<br>
