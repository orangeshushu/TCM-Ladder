from llmtuner import ChatModel
import pandas as pd
import os
import time
import requests
import json
from tqdm import tqdm

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
    prompt = f"""。
        问题: {question}
        选项:
        {options_text}
       """

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

    chat_model = ChatModel()

    # 处理每个问题
    for idx in range(len(df)):
        question = df.loc[idx, "question"]

        prompt = f"请回答以下填空题，补充()中的部分：{question},仅给出填空的答案"

        response = ""
        for new_text in chat_model.stream_chat(prompt):
            response += new_text

        # 提取答案并保存
        df.loc[idx, "zhongjing_response"] = response

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

# def main():
#     chat_model = ChatModel()
#     history = []
#     print("Welcome to the CLI application, use `clear` to remove the history, use `exit` to exit the application.")
#
#     # while True:
#     #     try:
#     #         # query = input("\nUser: ")
#     #         query = ('请回答以下选择题：首先提出“六气者从火化”观点的专家是	a朱丹溪	b张元素	c李杲	d刘完素')
#     #     except UnicodeDecodeError:
#     #         print("Detected decoding error at the inputs, please set the terminal encoding to utf-8.")
#     #         continue
#     #     except Exception:
#     #         raise
#     #
#     #     if query.strip() == "exit":
#     #         break
#     #
#     #     if query.strip() == "clear":
#     #         history = []
#     #         print("History has been removed.")
#     #         continue
#     #
#     #     print("Assistant: ", end="", flush=True)
#     #
#     #     response = ""
#     #     for new_text in chat_model.stream_chat(query, history):
#     #         print(new_text, end="", flush=True)
#     #         response += new_text
#     #     print()
#     #
#     #     history = history + [(query, response)]
#
#     response = ""
#     query =("周围性神经炎能治好吗？")
#     for new_text in chat_model.stream_chat(query, history):
#         print(new_text, end="", flush=True)


if __name__ == "__main__":
    process_questions('/cluster/pixstor/xudong-lab/yangyu/TCM/填空/内科学_填空.xlsx','/cluster/pixstor/xudong-lab/yangyu/TCM/填空/内科学_填空_zhongjing.xlsx')
    # main()