import os
import random
import csv
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator

# ---------------- Step 1: Detect Chinese Font ----------------
def find_chinese_font():
    possible_paths = [
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

font_path = find_chinese_font()
if font_path is None:
    raise RuntimeError("Chinese font not found")

font = ImageFont.truetype(font_path, 24)
title_font = ImageFont.truetype(font_path, 28)

# ---------------- Step 2: Initialize Directories and Files ----------------
herb_folder = 'herbs'
output_folder = 'questions_english'
os.makedirs(output_folder, exist_ok=True)

image_files = [f for f in os.listdir(herb_folder) if f.lower().endswith('.jpg')]
assert len(image_files) >= 4, "At least 4 different herb images are required"

herb_names = [os.path.splitext(f)[0] for f in image_files]

# ---------------- Step 3: Translate Herb Names Using googletrans ----------------
translator = Translator()
herb_dict = {}
print("Translating herb names...")
for name in herb_names:
    print(name)
    try:
        translated = translator.translate(name, src='zh-CN', dest='en').text
        print(translated)
        herb_dict[name] = translated
    except Exception as e:
        herb_dict[name] = name  # fallback
        print(f"Translation failed: {name}, using original name. Error: {e}")

print("Translation completed:")
print(herb_dict)

# ---------------- Step 4: Initialize CSV Files ----------------
answer_csv = open(os.path.join(output_folder, 'answers.csv'), 'w', newline='', encoding='utf-8-sig')
raw_en_csv = open(os.path.join(output_folder, 'raw_en.csv'), 'w', newline='', encoding='utf-8-sig')

answer_writer = csv.writer(answer_csv)
raw_en_writer = csv.writer(raw_en_csv)

answer_writer.writerow(['id', 'answer'])
raw_en_writer.writerow(['id', 'question', 'A', 'B', 'C', 'D', 'answer'])

# ---------------- Step 5: Generate Each Question ----------------
option_labels = ['A', 'B', 'C', 'D']
img_size = 256
spacing_x = 20
spacing_y = 30
canvas_width = 600
canvas_height = 700

for idx, correct_file in enumerate(image_files):
    question_id = f"{idx+1:04d}"
    correct_name = os.path.splitext(correct_file)[0]
    english_correct = herb_dict.get(correct_name, correct_name)
    question_text = f"Which of the following herbs is {english_correct}?"

    distractors = random.sample([f for f in image_files if f != correct_file], 3)
    options = [correct_file] + distractors
    random.shuffle(options)
    correct_index = options.index(correct_file)
    correct_label = option_labels[correct_index]

    option_names_zh = [os.path.splitext(f)[0] for f in options]
    option_names_en = [herb_dict.get(n, n) for n in option_names_zh]

    images = [Image.open(os.path.join(herb_folder, f)).resize((img_size, img_size)) for f in options]

    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)

    bbox = draw.textbbox((0, 0), question_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    draw.text(((canvas_width - text_width) // 2, 20), question_text, fill='black', font=title_font)

    x1 = (canvas_width - (img_size * 2 + spacing_x)) // 2
    positions = [
        (x1, 80), (x1 + img_size + spacing_x, 80),
        (x1, 80 + img_size + spacing_y), (x1 + img_size + spacing_x, 80 + img_size + spacing_y)
    ]

    for i, (img, pos) in enumerate(zip(images, positions)):
        canvas.paste(img, pos)
        label = option_labels[i]
        label_bbox = draw.textbbox((0, 0), label, font=font)
        label_width = label_bbox[2] - label_bbox[0]
        label_x = pos[0] + img_size // 2 - label_width // 2
        draw.text((label_x, pos[1] + img_size + 5), label, fill='black', font=font)

    save_path = os.path.join(output_folder, f"{question_id}.jpg")
    canvas.save(save_path)

    answer_writer.writerow([question_id, correct_label])
    raw_en_writer.writerow([question_id, question_text] + option_names_en + [correct_label])
    print(f"✅ {question_id}.jpg generated - Answer: {correct_label} ({english_correct})")

# ---------------- Step 6: Close Files ----------------
answer_csv.close()
raw_en_csv.close()
print("\n All English visual questions have been generated and saved in the questions/ folder")
