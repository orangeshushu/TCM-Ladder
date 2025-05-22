import pandas as pd
import os
import time
import google.generativeai as genai
from tqdm import tqdm
from PIL import Image

# Gemini API 设置
GEMINI_API_KEY = "AIzaSyDBlX4nORi4fXBt000SA-on8Qa4G-h9zq4"  # 替换为你的 API 密钥
MODEL_NAME = "gemini-2.0-flash"

# 配置 Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)


def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return None


def create_prompt(question, options):
    valid_options = {k: v for k, v in options.items() if isinstance(v, str)}
    options_text = ""
    for option_key, option_value in valid_options.items():
        options_text += f"{option_key}. {option_value}\n"

    prompt = f"""请回答以下选择题，并明确指出你认为正确的选项字母（A、B、C、D或E）。
问题: {question}
选项:
{options_text}
请直接以"答案:选项字母"的格式回答，例如"答案:A"。"""
    return prompt


def call_gemini_api(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"调用Gemini API时出错: {e}")
        time.sleep(10)
        return "API调用失败"


def extract_answer(response):
    if "答案:" in response:
        parts = response.split("答案:")
        if len(parts) > 1:
            answer = parts[1].strip()
            return answer[0].upper() if answer else "未能提取答案"

    for letter in ["A", "B", "C", "D", "E"]:
        if f"选项{letter}" in response or f"选{letter}" in response or f"答案是{letter}" in response or f"答案{letter}" in response:
            return letter

    lines = response.split("\n")
    for line in lines:
        clean_line = line.strip()
        if clean_line in ["A", "B", "C", "D", "E"]:
            return clean_line

    return f"无法自动提取答案，原始回答: {response}"


def process_questions(file_path, output_path=None):
    df = read_excel(file_path)
    if df is None:
        return

    required_columns = ["question", "A", "B", "C", "D"]
    for col in required_columns:
        if col not in df.columns:
            print(f"错误: 缺少必要的列 '{col}'")
            return

    df["gemini_response"] = ""
    df["extracted_answer"] = ""

    for idx in tqdm(range(len(df)), desc="处理问题"):
        question = df.loc[idx, "question"]
        options = {
            "A": df.loc[idx, "A"],
            "B": df.loc[idx, "B"],
            "C": df.loc[idx, "C"],
            "D": df.loc[idx, "D"]
        }
        if "E" in df.columns and isinstance(df.loc[idx, "E"], str):
            options["E"] = df.loc[idx, "E"]

        prompt = create_prompt(question, options)
        response = call_gemini_api(prompt)

        df.loc[idx, "gemini_response"] = response
        df.loc[idx, "extracted_answer"] = extract_answer(response)

        if idx % 50 == 0 and idx > 0:
            if output_path:
                df.to_excel(output_path, index=False)
                print(f"已保存进度，完成 {idx} 个问题")
            time.sleep(2)

    if output_path is None:
        output_path = file_path.replace(".xlsx", "_gemini.xlsx")
        if output_path == file_path:
            output_path = f"{file_path}_gemini.xlsx"

    df.to_excel(output_path, index=False)
    print(f"所有问题处理完成，结果已保存至: {output_path}")
    return output_path


if __name__ == "__main__":
    input_file = 'test/中医基础学_assistant.xlsx'
    if not os.path.exists(input_file):
        print(f"错误: 文件 '{input_file}' 不存在")
    else:
        output_file = input_file.replace(".xlsx", "_gemini.xlsx")
        result_file = process_questions(input_file, output_file)
        if result_file:
            print(f"处理完成! 结果保存在: {result_file}")
