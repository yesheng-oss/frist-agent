import requests
import json
import re
from typing import List, Dict, Any, Optional, Callable

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL = "llama3.2:latest"

class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def to_json(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description
        }

class OllamaAgent:
    def __init__(self, model: str = MODEL):
        self.model = model
        self.tools: Dict[str, Tool] = {}
        self.messages: List[Dict] = []
        self.max_iterations = 10

    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def chat(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        for _ in range(self.max_iterations):
            response = self._generate()
            if response.startswith("ACTION:"):
                result = self._execute_action(response)
                if result is None:
                    break
                self.messages.append({"role": "user", "content": f"RESULT: {result}"})
            else:
                self.messages.append({"role": "assistant", "content": response})
                return response
        return "Unable to complete the task."

    def _generate(self) -> str:
        tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools.values()])
        system_prompt = f"""你是一个智能助手，可以使用工具完成任务。

可用工具:
{tool_desc}

当需要使用工具时，请按以下格式回复:
ACTION: tool_name | param1=value1 | param2=value2

当完成任务时，直接回复结果，不要使用上述格式。

可用工具列表: {list(self.tools.keys())}"""

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + self.messages[-6:],
            "stream": False
        }

        response = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]

    def _execute_action(self, action_str: str) -> Optional[str]:
        match = re.match(r"ACTION:\s*(\w+)\s*(.*)", action_str)
        if not match:
            return None

        tool_name, params_str = match.groups()
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"

        params = {}
        for param in params_str.split("|"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key.strip()] = value.strip()

        try:
            result = self.tools[tool_name].func(**params)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"

def create_search_tool():
    return Tool(
        name="search",
        description="搜索网络获取信息",
        func=lambda query: f"搜索结果: {query} - 请检查搜索结果"
    )

def createCalculatorTool():
    def calc(expression: str) -> str:
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except:
            return "计算表达式无效"

    return Tool(
        name="calculate",
        description="计算数学表达式",
        func=calc
    )

if __name__ == "__main__":
    agent = OllamaAgent()
    agent.add_tool(create_search_tool())
    agent.add_tool(createCalculatorTool())

    print("=" * 50)
    print("智能体已启动 (输入 'quit' 退出)")
    print("=" * 50)

    while True:
        user_input = input("\n你: ")
        if user_input.lower() == "quit":
            break

        response = agent.chat(user_input)
        print(f"\n智能体: {response}")