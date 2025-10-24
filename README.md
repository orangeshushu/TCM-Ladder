# TCM-Ladder: A Benchmark for Multimodal Question Answering on Traditional Chinese Medicine

## 📌 Abstract

TCM-Ladder, the first comprehensive multimodal QA dataset specifically designed for evaluating large TCM language models. 

- Multiple core disciplines of TCM: fundamental theory, diagnostics, herbal formulas, internal medicine, surgery, pharmacognosy, and pediatrics. 

- Multimodal: TCM-Ladder incorporates various modalities such as images and videos. 

- Multiple question formats: single-choice, multiple-choice, fill-in-the-blank, diagnostic dialogue, and visual comprehension tasks. 

We trained a reasoning model on TCM-Ladder and conducted comparative experiments against nine state-of-the-art general domain and five leading TCM-specific LLMs to evaluate their performance on the dataset. Moreover, we propose Ladder-Score, an evaluation method specifically designed for TCM question answering that effectively assesses answer quality in terms of terminology usage and semantic expression. To the best of our knowledge, this is the first work to systematically evaluate mainstream general domain and TCM-specific LLMs on a unified multimodal benchmark. The datasets and leaderboard are publicly available at https://tcmladder.com and will be continuously updated. 


> 📑 [paper](https://arxiv.org/abs/2505.24063) 📖 [dataset](https://huggingface.co/datasets/timzzyus/TCM-Ladder)


## 🚀 News
- [2025-9] Our paper is accepted by **NeurIPS 2025**.
- [2025-5] We release our preprint paper on arXiv.
- [2025-5] Our dataset TCM-Ladder is released on **Huggingface**.

  

## 📝 TODOs

- [x] English version.
- [x] Instructions to run evaluation. 


### 1. Overview of the architectural composition of TCM-Ladder.
 
![New Figure 1](https://github.com/user-attachments/assets/0db686f0-c0af-4413-a596-cf2ae0d4c596)


### 2.Data distribution and length statistics in TCM-Ladder

![Final Figure 2](https://github.com/user-attachments/assets/9cb5e5b5-5331-43ec-9006-dd53a1805a47)

### 3. Performance of general-domain and TCM-specific language models on single and multiple-choice question answering tasks

![Performance](https://github.com/user-attachments/assets/0ef32730-6a95-4f8b-9654-e0dd7a432f37)

### 4. The performance of large language models on questions regarding Chinese herbal medicine and tongue images.

![Performance](https://github.com/user-attachments/assets/fbe8c013-900e-44de-a4f8-2d33b2e13dda)

## 🌟Citation
if you find our work useful in your research, please consider citing:
```bibtex
@article{xie2025tcm,
  title={TCM-Ladder: A Benchmark for Multimodal Question Answering on Traditional Chinese Medicine},
  author={Xie, Jiacheng and Yu, Yang and Zhang, Ziyang and Zeng, Shuai and He, Jiaxuan and Vasireddy, Ayush and Tang, Xiaoting and Guo, Congyu and Zhao, Lening and Jing, Congcong and others},
  journal={arXiv preprint arXiv:2505.24063},
  year={2025}
}
```


