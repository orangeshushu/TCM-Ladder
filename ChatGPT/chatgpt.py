import pandas as pd
import os
import time
import requests
import json
from tqdm import tqdm

# OpenAI API设置
OPENAI_API_KEY = "" 
API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-4o"  # 或其他适用的模型如 "gpt-3.5-turbo"


def read_excel(file_path):
    """读取Excel文件并返回DataFrame"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


def create_prompt(question, options):
    """创建发送给ChatGPT的prompt"""
    # 过滤掉NaN选项
    valid_options = {k: v for k, v in options.items() if isinstance(v, str)}

    # 构建选项文本
    options_text = ""
    for option_key, option_value in valid_options.items():
        options_text += f"{option_key}. {option_value}\n"

    # 构建完整prompt
    prompt = f"""请回答以下选择题，并明确指出你认为正确的选项字母（A、B、C、D或E）。
    问题: {question}
    选项:
    {options_text}
    请直接以"答案:选项字母"的格式回答，例如"答案:A"。"""

    return prompt


def call_chatgpt_api(prompt):
    """调用ChatGPT API获取回答"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"调用API时出错: {e}")
        # 如果是速率限制错误，等待并重试
        if "rate limit" in str(e).lower():
            print("达到API速率限制，等待20秒后重试...")
            time.sleep(20)
            return call_chatgpt_api(prompt)
        return "API调用失败"


def extract_answer(response):
    """从ChatGPT回答中提取选项字母"""
    # 尝试查找"答案:X"模式
    if "答案:" in response:
        parts = response.split("答案:")
        if len(parts) > 1:
            answer = parts[1].strip()
            # 取第一个字母（假设是选项字母）
            return answer[0].upper() if answer else "未能提取答案"

    # 如果找不到标准格式，查找任何独立的选项字母
    for letter in ["A", "B", "C", "D", "E"]:
        if f"选项{letter}" in response or f"选{letter}" in response or f"答案是{letter}" in response or f"答案{letter}" in response:
            return letter

    # 最后检查是否有单独的选项字母
    lines = response.split("\n")
    for line in lines:
        clean_line = line.strip()
        if clean_line in ["A", "B", "C", "D", "E"]:
            return clean_line

    # 返回整个回答，以便手动检查
    return f"无法自动提取答案，原始回答: {response}"


def process_questions(file_path, output_path=None):
    """处理Excel中的所有问题并保存结果"""
    df = read_excel(file_path)

    if df is None:
        return

    # 检查必要的列是否存在
    required_columns = ["question", "A", "B", "C", "D"]
    for col in required_columns:
        if col not in df.columns:
            print(f"错误: 缺少必要的列 '{col}'")
            return

    # 创建存储答案的列
    df["chatgpt_response"] = ""
    df["extracted_answer"] = ""

    # 处理每个问题
    for idx in tqdm(range(len(df)), desc="处理问题"):
        question = df.loc[idx, "question"]

        # 获取所有选项
        options = {
            "A": df.loc[idx, "A"],
            "B": df.loc[idx, "B"],
            "C": df.loc[idx, "C"],
            "D": df.loc[idx, "D"]
        }

        # 如果E选项存在，也包括它
        if "E" in df.columns and isinstance(df.loc[idx, "E"], str):
            options["E"] = df.loc[idx, "E"]

        # 创建prompt并调用API
        prompt = create_prompt(question, options)
        response = call_chatgpt_api(prompt)

        # 提取答案并保存
        df.loc[idx, "chatgpt_response"] = response
        df.loc[idx, "extracted_answer"] = extract_answer(response)

        # 每10个问题保存一次进度
        if idx % 50 == 0 and idx > 0:
            if output_path:
                df.to_excel(output_path, index=False)
                print(f"已保存进度，完成 {idx} 个问题")

            # 防止API速率限制
            time.sleep(2)

    # 保存最终结果
    if output_path is None:
        output_path = file_path.replace(".xlsx", "_with_answers.xlsx")
        if output_path == file_path:  # 如果文件没有.xlsx后缀
            output_path = f"{file_path}_with_answers.xlsx"

    df.to_excel(output_path, index=False)
    print(f"所有问题处理完成，结果已保存至: {output_path}")
    return output_path


if __name__ == "__main__":
    # 用户输入文件路径
    input_file = 'test/中医基础学_assistant.xlsx'

    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 文件 '{input_file}' 不存在")
    else:
        # 询问输出文件路径（可选）
        output_file = input_file.replace(".xlsx", "_4o.xlsx")
        if not output_file:
            output_file = None

        # 处理问题
        result_file = process_questions(input_file, output_file)
        if result_file:
            print(f"处理完成! 结果保存在: {result_file}")