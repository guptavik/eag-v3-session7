# Corpus Manifest

55 AI/ML paper summaries indexed by the Session 7 RAG agent. Each file follows the
same template (`Title / Year` · `Problem` · `Method` · `Key contributions` · `Results`),
~200–350 words, so it chunks cleanly into the agent's 400-word windows and gives
semantic queries reliable concept density.

The five files also present under `sandbox/papers/` (attention, cot, dpo, lora, react)
back the **base** queries E–H; the full set here backs the **5 custom** queries.

| # | filename | title | year | tags |
|---|----------|-------|------|------|
| 1 | attention.md | Attention Is All You Need | 2017 | transformer, attention |
| 2 | bert.md | BERT: Pre-training of Deep Bidirectional Transformers | 2018 | pretraining, nlp |
| 3 | gpt3.md | Language Models are Few-Shot Learners (GPT-3) | 2020 | llm, few-shot |
| 4 | resnet.md | Deep Residual Learning (ResNet) | 2015 | vision, residual |
| 5 | word2vec.md | Efficient Estimation of Word Representations (word2vec) | 2013 | embeddings |
| 6 | seq2seq.md | Sequence to Sequence Learning with Neural Networks | 2014 | seq2seq |
| 7 | lstm.md | Long Short-Term Memory | 1997 | rnn, memory |
| 8 | dropout.md | Dropout: Preventing Overfitting | 2014 | regularization |
| 9 | batchnorm.md | Batch Normalization | 2015 | training, normalization |
| 10 | layernorm.md | Layer Normalization | 2016 | training, normalization |
| 11 | adam.md | Adam: A Method for Stochastic Optimization | 2014 | optimizer |
| 12 | gan.md | Generative Adversarial Networks | 2014 | generative |
| 13 | vae.md | Auto-Encoding Variational Bayes (VAE) | 2013 | generative |
| 14 | unet.md | U-Net: Biomedical Image Segmentation | 2015 | vision, segmentation |
| 15 | vit.md | An Image is Worth 16x16 Words (ViT) | 2020 | vision, transformer |
| 16 | cot.md | Chain-of-Thought Prompting | 2022 | reasoning, prompting |
| 17 | react.md | ReAct: Synergizing Reasoning and Acting | 2022 | reasoning, agents |
| 18 | scratchpad.md | Show Your Work: Scratchpads | 2021 | reasoning |
| 19 | self_consistency.md | Self-Consistency Improves Chain-of-Thought | 2022 | reasoning |
| 20 | tot.md | Tree of Thoughts | 2023 | reasoning, search |
| 21 | least_to_most.md | Least-to-Most Prompting | 2022 | reasoning, prompting |
| 22 | toolformer.md | Toolformer: LMs Can Use Tools | 2023 | agents, tools |
| 23 | reflexion.md | Reflexion: Verbal Reinforcement Learning | 2023 | agents, reasoning |
| 24 | instructgpt.md | InstructGPT: Following Instructions with Human Feedback | 2022 | rlhf, alignment |
| 25 | dpo.md | Direct Preference Optimization | 2023 | alignment, preference |
| 26 | ppo.md | Proximal Policy Optimization | 2017 | rl, policy |
| 27 | rlhf_summarize.md | Learning to Summarize from Human Feedback | 2020 | rlhf, alignment |
| 28 | constitutional_ai.md | Constitutional AI | 2022 | alignment, safety |
| 29 | kto.md | KTO: Prospect-Theoretic Optimization | 2024 | alignment, preference |
| 30 | lora.md | LoRA: Low-Rank Adaptation | 2021 | peft, efficiency |
| 31 | qlora.md | QLoRA: Finetuning of Quantized LLMs | 2023 | peft, quantization |
| 32 | adapters.md | Parameter-Efficient Transfer Learning (Adapters) | 2019 | peft |
| 33 | prefix_tuning.md | Prefix-Tuning | 2021 | peft, prompting |
| 34 | prompt_tuning.md | The Power of Scale for Prompt Tuning | 2021 | peft, prompting |
| 35 | distillation.md | Distilling the Knowledge in a Neural Network | 2015 | compression |
| 36 | llm_int8.md | LLM.int8(): 8-bit Matrix Multiplication | 2022 | quantization |
| 37 | flashattention.md | FlashAttention | 2022 | efficiency, attention |
| 38 | moe.md | Sparsely-Gated Mixture-of-Experts | 2017 | scaling, moe |
| 39 | switch_transformer.md | Switch Transformers | 2021 | scaling, moe |
| 40 | rag.md | Retrieval-Augmented Generation | 2020 | retrieval, rag |
| 41 | dpr.md | Dense Passage Retrieval | 2020 | retrieval |
| 42 | realm.md | REALM: Retrieval-Augmented Pre-Training | 2020 | retrieval, rag |
| 43 | fid.md | Fusion-in-Decoder | 2020 | retrieval, rag |
| 44 | colbert.md | ColBERT: Late Interaction Passage Search | 2020 | retrieval |
| 45 | faiss.md | Billion-Scale Similarity Search (FAISS) | 2017 | retrieval, ann |
| 46 | scaling_laws.md | Scaling Laws for Neural Language Models | 2020 | scaling |
| 47 | chinchilla.md | Training Compute-Optimal LLMs (Chinchilla) | 2022 | scaling |
| 48 | t5.md | Unified Text-to-Text Transformer (T5) | 2019 | pretraining |
| 49 | palm.md | PaLM: Scaling with Pathways | 2022 | llm, scaling |
| 50 | llama.md | LLaMA: Open Foundation Models | 2023 | llm |
| 51 | clip.md | Learning Transferable Visual Models (CLIP) | 2021 | multimodal, vision |
| 52 | dalle.md | Zero-Shot Text-to-Image Generation (DALL-E) | 2021 | multimodal, generative |
| 53 | flamingo.md | Flamingo: a Visual Language Model | 2022 | multimodal |
| 54 | whisper.md | Robust Speech Recognition (Whisper) | 2022 | speech |
| 55 | ddpm.md | Denoising Diffusion Probabilistic Models | 2020 | generative, diffusion |
