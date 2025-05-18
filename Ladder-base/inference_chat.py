from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

system_prompt = "You are a helpful AI Assistant that provides well-reasoned and detailed responses. You first think about the reasoning process as an internal monologue and then provide the user with the answer. The response cannot be more than 400 words. Each question has only one answer, A-E. Respond in the following format: <think>\n...\n</think>\n<answer>\n...答案:A-E...\n</answer>. Do not respond with another tag. Do not repeat the response."

# Load the tokenizer and model
model_name = "ashuai81/Qwen2.5-7B-CTM"
# model_name = "data/Qwen2.5-7B-Instruct-GRPO"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE)

user_input = """
肾病患儿面目皆肿，以下肢为甚，面白无华，畏寒肢冷，神疲蜷卧，纳少便溏，舌淡胖，苔白滑，脉沉细无力，证属：

A.脾虚湿困
B.脾肾阳虚
C.肝肾阴虚
D.气滞血瘀
E.肺脾气虚
"""
formatted_input = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
inputs = tokenizer(formatted_input, return_tensors="pt").to(DEVICE)

output = model.generate(inputs.input_ids, 
                        attention_mask=inputs.attention_mask,
                        max_length=512, do_sample=False)
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
assistant_response = generated_text.split("assistant\n")[-1]

print(f"\nAssistant: {assistant_response}")
# Assistant: <think>
# 肾病患儿面目皆肿，以下肢为甚，这种情况常提示体内存在水液代谢紊乱的问题。面白无华，畏寒肢冷，神疲蜷卧，纳少便溏，舌淡胖，苔白滑，脉沉细无力等表现更多地指示出孩子的体质状况可能是气机运行受阻和阳气不足。脾肾的功能在这些症状中显得尤为重要。
# </think>
# <answer>
# B
# </answer>

