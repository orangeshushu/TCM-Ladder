import sys
import json
import fire
import gradio as gr
import torch
import transformers
from peft import PeftModel
from transformers import GenerationConfig, AutoModelForCausalLM, AutoTokenizer

from utils.prompter import Prompter
import pandas as pd
import time
import requests

from tqdm import tqdm

if torch.cuda.is_available():
    device = "cuda"

def load_instruction(instruct_dir):
    input_data = []
    with open(instruct_dir, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            d = json.loads(line)
            input_data.append(d)
    return input_data

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
    # prompt = []
    # prompt = f"""
    #          请回答以下选择题，并明确指出你认为正确的选项字母（A、B、C、D或E）。
    #         问题: {question}
    #         选项:
    #         {options_text}
    #         请直接回答选项，例如"答案:A"。
    #         """

    prompt = f"""
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
        if f"选项{letter}" in response or f"选{letter}" in response or f"答案是{letter}" in response or f"答案{letter}" in response or f"答案为{letter}" in response:
            return letter

    # 最后检查是否有单独的选项字母
    lines = response.split("\n")
    for line in lines:
        clean_line = line.strip()
        if clean_line in ["A", "B", "C", "D", "E"]:
            return clean_line

    # 返回整个回答，以便手动检查
    return f"无法自动提取答案，原始回答: {response}"

def main(
    load_8bit: bool = False,
    base_model: str = "",
    # the infer data, if not exists, infer the default instructions in code
    instruct_dir: str = "",
    use_lora: bool = True,
    lora_weights: str = "tloen/alpaca-lora-7b",
    # The prompt template to use, will default to med_template.
    prompt_template: str = "med_template",
):
    prompter = Prompter(prompt_template)
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        load_in_8bit=load_8bit,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    if use_lora:
        print(f"using lora {lora_weights}")
        model = PeftModel.from_pretrained(
            model,
            lora_weights,
            torch_dtype=torch.float16,
        )
    # unwind broken decapoda-research config
    model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
    model.config.bos_token_id = 1
    model.config.eos_token_id = 2
    if not load_8bit:
        model.half()  # seems to fix bugs for some users.

    model.eval()

    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)

    def evaluate(
        instruction,
        input=None,
        temperature=0.1,
        top_p=0.75,
        top_k=40,
        num_beams=4,
        max_new_tokens=256,
        **kwargs,
    ):
        prompt = prompter.generate_prompt(instruction, input)
        inputs = tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(device)
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_beams=num_beams,
            **kwargs,
        )
        with torch.no_grad():
            generation_output = model.generate(
                input_ids=input_ids,
                generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = tokenizer.decode(s)
        return prompter.get_response(output)

    def infer_from_json(instruct_dir):
        input_data = load_instruction(instruct_dir)
        for d in input_data:
            instruction = d["instruction"]
            output = d["output"]
            print("###infering###")
            model_output = evaluate(instruction)
            print("###instruction###")
            print(instruction)
            print("###golden output###")
            print(output)
            print("###model output###")
            print(model_output)

    # if instruct_dir != "":
    #     infer_from_json(instruct_dir)
    # else:
    #     for instruction in [
    #         "我感冒了，怎么治疗",
    #         "一个患有肝衰竭综合征的病人，除了常见的临床表现外，还有哪些特殊的体征？",
    #         "急性阑尾炎和缺血性心脏病的多发群体有何不同？",
    #         "小李最近出现了心动过速的症状，伴有轻度胸痛。体检发现P-R间期延长，伴有T波低平和ST段异常",
    #     ]:
    #         print("Instruction:", instruction)
    #         print("Response:", evaluate(instruction))
    #         print()
    file_path = '/cluster/pixstor/xudong-lab/yangyu/TCM/test/儿科学_assistant.xlsx'
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
        response = evaluate(prompt)

        df.loc[idx, "huatuo_response"] = response
        df.loc[idx, "extracted_answer"] = extract_answer(response)

        output_path = file_path.replace(".xlsx", "_bentsao.xlsx")

        # 每10个问题保存一次进度
        if idx % 50 == 0 and idx > 0:
            if output_path:
                df.to_excel(output_path, index=False)
                print(f"已保存进度，完成 {idx} 个问题", flush=True)

    df.to_excel(output_path, index=False)
    print(f"所有问题处理完成，结果已保存至: {output_path}")
    return output_path



if __name__ == "__main__":
    fire.Fire(main)
