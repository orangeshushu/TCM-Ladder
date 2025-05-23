import os
import random
import csv
from PIL import Image, ImageDraw, ImageFont

# ----------- Step 1: Automatically detect Chinese font -----------
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
    raise RuntimeError("Chinese font not found, please specify the path manually")

font = ImageFont.truetype(font_path, 24)
title_font = ImageFont.truetype(font_path, 28)

# ----------- Step 2: Path setup and initialization -----------
herb_folder = 'herb_final'
output_folder = 'questions_final'
os.makedirs(output_folder, exist_ok=True)

image_files = [f for f in os.listdir(herb_folder) if f.lower().endswith('.jpg')]
assert len(image_files) >= 4, "At least 4 images are required"

# ----------- Step 3: Prepare CSV files -----------
answer_csv_path = os.path.join(output_folder, 'answers.csv')
raw_csv_path = os.path.join(output_folder, 'raw.csv')

answer_csv = open(answer_csv_path, mode='w', newline='', encoding='utf-8-sig')
raw_csv = open(raw_csv_path, mode='w', newline='', encoding='utf-8-sig')

answer_writer = csv.writer(answer_csv)
raw_writer = csv.writer(raw_csv)

answer_writer.writerow(['id', 'answer'])
raw_writer.writerow(['id', 'question', 'A', 'B', 'C', 'D', 'answer'])

# ----------- Step 4: Start generating questions -----------
option_labels = ['A', 'B', 'C', 'D']
img_size = 256
spacing_x = 20
spacing_y = 30
canvas_width = 600
canvas_height = 700

for idx, correct_file in enumerate(image_files):
    question_id = f"{idx+1:04d}"
    correct_name = os.path.splitext(correct_file)[0]
    question_text = f"Which of the following herbs is '{correct_name}'?"

    distractors = random.sample([f for f in image_files if f != correct_file], 3)
    options = [correct_file] + distractors
    random.shuffle(options)
    correct_index = options.index(correct_file)
    correct_label = option_labels[correct_index]

    option_names = [os.path.splitext(f)[0] for f in options]
    images = [Image.open(os.path.join(herb_folder, f)).resize((img_size, img_size)) for f in options]

    # Create canvas and draw question text
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

    # Save the question image
    save_path = os.path.join(output_folder, f"{question_id}.jpg")
    canvas.save(save_path)

    # Write to CSV files
    answer_writer.writerow([question_id, correct_label])
    raw_writer.writerow([question_id, question_text] + option_names + [correct_label])

    print(f"✅ Question {question_id}.jpg generated, correct answer: {correct_label} ({correct_name})")

# ----------- Step 5: Close CSV files -----------
answer_csv.close()
raw_csv.close()
print(f"\nAll question images are saved in 'questions/', answers in 'answers.csv', and raw data in 'raw.csv'")
