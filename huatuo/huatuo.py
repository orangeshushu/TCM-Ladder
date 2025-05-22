import torch

from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import pandas as pd
import time
import requests
import json
from tqdm import tqdm

os.environ['TRANSFORMERS_CACHE'] = '/cluster/pixstor/xudong-lab/yangyu/TCM'
# messages = []
# messages.append({"role": "user", "content": "请回答以下选择题：首先提出“六气者从火化”观点的专家是	a朱丹溪	b张元素	c李杲	d刘完素"})
# response = model.HuatuoChat(tokenizer, messages)
# print(response)

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
    # prompt = f"""请根据你已有的知识回答该选择题，并明确指出你认为正确的选项字母（A、B、C、D或E）。
    # 问题: {question}
    # 选项:
    # {options_text}
    # 请直接以"答案:选项字母"的格式回答，例如"答案:A"。"""
    prompt = []
    prompt.append({"role": "user",
                     "content": f"""
                     请回答以下选择题，并明确指出你认为正确的选项字母（A、B、C、D或E）。
                    问题: {question}
                    选项:
                    {options_text}
                    请直接回答选项，例如"A"。
                   """})

    # prompt = f"""
    #     问题: {question}
    #     选项:
    #     {options_text}
    #    """

    return prompt

def extract_answer(response):
    """从ChatGPT回答中提取选项字母"""
    # 尝试查找"答案:X"模式
    # if "答案:" in response:
    #     parts = response.split("答案:")

    if response[0].upper() in ["A", "B", "C", "D", "E"]:

        # 取第一个字母（假设是选项字母）
        return response[0].upper()

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
    df["huatuo_response"] = ""
    df["extracted_answer"] = ""


    # 处理每个问题
    for idx in range(len(df)):
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


        prompt = create_prompt(question, options)
        response = model.HuatuoChat(tokenizer, prompt)

        # 提取答案并保存
        df.loc[idx, "huatuo_response"] = response
        df.loc[idx, "extracted_answer"] = extract_answer(response)

        # 每10个问题保存一次进度
        if idx % 50 == 0 and idx > 0:
            if output_path:
                df.to_excel(output_path, index=False)
                print(f"已保存进度，完成 {idx} 个问题", flush=True)


    # 保存最终结果
    if output_path is None:
        output_path = file_path.replace(".xlsx", "_with_answers.xlsx")
        if output_path == file_path:  # 如果文件没有.xlsx后缀
            output_path = f"{file_path}_with_answers.xlsx"

    df.to_excel(output_path, index=False)
    print(f"所有问题处理完成，结果已保存至: {output_path}")
    return output_path


if __name__ == "__main__":
    tokenizer = AutoTokenizer.from_pretrained("FreedomIntelligence/HuatuoGPT2-7B", use_fast=True,
                                              trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained("FreedomIntelligence/HuatuoGPT2-7B", device_map="auto",
                                                 torch_dtype=torch.bfloat16, trust_remote_code=True)

    process_questions('/cluster/pixstor/xudong-lab/yangyu/TCM/test/中医基础学_assistant.xlsx',
                      '/cluster/pixstor/xudong-lab/yangyu/TCM/test/中医基础学_assistant_huatuo.xlsx')
