# Automatic Summarization of BOE Scholarship Announcements

## Overview
This project implements an automatic summarization system combining information extraction (NLU) and abstractive text generation (NLG). Given a corpus of BOE scholarship announcements in PDF format, the system extracts structured information and generates a concise abstractive summary.

## Objectives
- Extract relevant scholarship information from PDF documents
- Store extracted data in a structured format (JSON / CSV / XML)
- Generate an abstractive summary using a generative language model
- Ensure the solution works across multiple documents

## Dataset
Five BOE PDF documents corresponding to scholarship announcements for academic years 2021–2022 through 2025–2026. The documents share a similar structure but are processed generically.

## Extracted Information
Examples of fields:
- Eligible educational programs
- Scholarship amounts
- Academic criteria
- Income thresholds
- Application deadlines

## Pipeline
1. PDF text extraction  
2. Information extraction  
3. Structured data storage  
4. Abstractive summary generation  

## Installation
### Project
```bash
git clone https://github.com/forteaj/summaryProject.git
cd summaryProject
pip install -r requirements.txt
```

### Ollama
```bash
# 1) Install Ollama
# Linux / MacOS
curl -fsSL https://ollama.com/install.sh | sh
# Windows
irm https://ollama.com/install.ps1 | iex

# 2) Pull the model (example: Qwen)
ollama pull qwen2.5:7b
```

## Usage
### Information Extraction
```bash
python -m information_extraction.extraction
```