# TTCM-Ladder: A Benchmark for Multimodal Question Answering on Traditional Chinese Medicine

## 📌 Abstract

Traditional Chinese Medicine (TCM), as an effective alternative medicine, has been receiving increasing attention. In recent years, the rapid development of large language models (LLMs) tailored for TCM has underscored the need for an objective and comprehensive evaluation framework to assess their performance on real-world tasks. However, existing evaluation datasets are limited in scope and primarily text-based, lacking a unified and standardized multimodal question-answering (QA) benchmark. To address this issue, we introduce TCM-Ladder, the first multimodal QA dataset specifically designed for evaluating large TCM language models. The dataset spans multiple core disciplines of TCM, including fundamental theory, diagnostics, herbal formulas, internal medicine, surgery, pharmacognosy, and pediatrics. In addition to textual content, TCM-Ladder incorporates various modalities such as images and videos. The datasets were constructed using a combination of automated and manual filtering processes and comprise 52,000+ questions in total. These questions include single-choice, multiple-choice, fill-in-the-blank, diagnostic dialogue, and visual comprehension tasks. We trained a reasoning model on TCM-Ladder and conducted comparative experiments against 9 state-of-the-art general domain and 5 leading TCM-specific LLMs to evaluate their performance on the datasets. Moreover, we propose Ladder-Score, an evaluation method specifically designed for TCM question answering that effectively assesses answer quality regarding terminology usage and semantic expression. To our knowledge, this is the first work to evaluate mainstream general domain and TCM-specific LLMs on a unified multimodal benchmark. The datasets and leaderboard are publicly available at https://tcmladder.com or https://54.211.107.106 and will be continuously updated. The source code is available at https://github.com/orangeshushu/TCM-Ladder.

### 1. Overview of the architectural composition of TCM-Ladder.
 
![figure1](https://github.com/orangeshushu/TCM-Ladder/blob/main/Figures/Figure%201.jpg)

> Figure 1.  TCM-Ladder encompasses six task types aimed at evaluating the comprehensive capabilities of large language models in Traditional Chinese Medicine. These include: (1) single-choice questions, which assess basic knowledge recognition; (2) multiple-choice questions, designed to test the model’s ability to integrate and reason over complex concepts; (3) long-form diagnostic question answering, which evaluates clinical reasoning based on detailed symptom descriptions and patient inquiries; (4) fill-in-the-blank tasks, which measure generative accuracy and contextual understanding without the aid of answer options; (5) image-based comprehension tasks, involving the interpretation of medicinal herb and tongue images to assess multimodal reasoning across visual and textual inputs; and (6) additional audio and video resources, such as diagnostic sounds, pulse recordings, and tuina (massage) videos, which support the development and evaluation of multimodal TCM models incorporating auditory and dynamic visual data.


### 2.Data distribution and length statistics in TCM-Ladder

![distribution](https://github.com/orangeshushu/TCM-Ladder/blob/main/Figures/Figure%202.jpg)

### 3. Performance of general-domain and TCM-specific language models on single and multiple-choice question answering tasks

![Performance](https://github.com/orangeshushu/TCM-Ladder/blob/main/Figures/Figure%203.png)



