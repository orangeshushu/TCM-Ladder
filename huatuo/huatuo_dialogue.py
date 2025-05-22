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


def process_questions(file_path, output_path=None):
    """处理Excel中的所有问题并保存结果"""
    df = read_excel(file_path)
    for idx in range(len(df)):
        question = df.loc[idx, "question"]
        prompt = []
        prompt.append({"role": "user",
                       "content": f"请回答以下填空题，补充()中的部分：{question},仅给出填空的部分"})
        response = model.HuatuoChat(tokenizer, prompt)

        # 提取答案并保存
        df.loc[idx, "huatuo_response"] = response

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

    process_questions('/cluster/pixstor/xudong-lab/yangyu/TCM/填空/内科学_填空.xlsx',
                      '/cluster/pixstor/xudong-lab/yangyu/TCM/填空/内科学_填空_huatuo.xlsx')
