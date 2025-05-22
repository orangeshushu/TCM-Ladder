import re
from functools import update_wrapper
from typing import Callable, Optional


def extract_answer(sentence: str) -> str | None:
    match = re.search(r'<answer>(.*?)</answer>', sentence, re.IGNORECASE | re.DOTALL)
    
    if match:
        answer_text = match.group(1)  
        option_match = re.search(r'([A-E])\b', answer_text, re.IGNORECASE)
        if option_match:
            return option_match.group(1).upper()
            
        patterns = [
            r'(?:正确答案是选|正确答案是|正确答案为|答案是|应该选|选择|答案为|应为|应选|正确选项是|答案：|答案:)\s*([A-E])',
            r'选\s*([A-E])\s*项',
            r'答案\s*([A-E])',
            r'为\s*([A-E])'
        ]
        
        for pattern in patterns:
            pattern_match = re.search(pattern, answer_text, re.IGNORECASE)
            if pattern_match:
                return pattern_match.group(1).upper()
    
    return None


def accuracy_reward_cn(completions: list[list[dict[str, str]]], solution: list[str], **kwargs) -> list[Optional[float]]:
    contents = [completion[0]["content"] for completion in completions]
    rewards = []
    for content, sol in zip(contents, solution):
        gold_parsed = sol.replace("$", "")
        if len(gold_parsed) != 0:
            answer_parsed = extract_answer(content)
            try:
                reward = float(gold_parsed == answer_parsed)
            except Exception as e:
                print(f"verify failed: {e}, answer: {answer_parsed}, gold: {gold_parsed}")
                reward = None
        else:
            reward = None
            print("Failed to parse gold solution: ", sol)
        rewards.append(reward)

    return rewards


def format_reward(completions, **kwargs):
    pattern = r"^<think>\n.*?\n</think>\n<answer>\n.*?\n</answer>$"
    completion_contents = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completion_contents]
    return [1.0 if match else 0.0 for match in matches]


def tag_count_reward(completions, **kwargs) -> list[float]:
    def count_tags(text: str) -> float:
        count = 0.0
        if text.count("<think>\n") == 1:
            count += 0.25
        if text.count("\n</think>\n") == 1:
            count += 0.25
        if text.count("\n<answer>\n") == 1:
            count += 0.25
        if text.count("\n</answer>") == 1:
            count += 0.25
        return count
    contents = [completion[0]["content"] for completion in completions]
    return [count_tags(c) for c in contents]


def get_code_format_reward(language: str = "python"):
    pattern = rf"^<think>\n.*?\n</think>\n<answer>\n.*?```{language}.*?```.*?\n</answer>$"
    def code_format_reward(completions, **kwargs):
        completion_contents = [completion[0]["content"] for completion in completions]
        matches = [re.match(pattern, content, re.DOTALL | re.MULTILINE) for content in completion_contents]
        return [1.0 if match else 0.0 for match in matches]

    return code_format_reward


def get_reward_funcs() -> list[Callable]:
    reward_funcs = [accuracy_reward_cn, format_reward, tag_count_reward]
    return reward_funcs
