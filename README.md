# Azure Cost CLI Tracker

A Python-based CLI tool for tracking and analyzing Azure cloud costs with AI-powered insights.

## Features

- 📊 **Cost Tracking**: Fetch and display Azure resource costs
- 🤖 **AI Analysis**: Get cost optimization recommendations using TinyLlama
- 🌐 **Portal Integration**: Open resources directly in Azure Portal
- 📈 **Category Summary**: Group costs by resource type
- 🎨 **Rich UI**: Beautiful terminal interface with tables and formatting

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install rich llama-cpp-python
   ```

2. **Download TinyLlama model:**
   ```bash
   curl -L -o models/tinyllama.gguf https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q2_K.gguf
   ```

3. **Install Azure CLI** (optional - demo mode available):
   ```bash
   winget install Microsoft.AzureCLI
   az login
   ```

4. **Run the tracker:**
   ```bash
   python azure_cost.py
   ```

## Testing

**Test the AI features:**
```bash
python test_llama.py
```

**Test the application:**
1. Run `python azure_cost.py`
2. Select option 1 to view costs
3. Select option 3 for AI analysis
4. Select option 4 for category summary
5. Select option 2 to test portal links

## Demo Mode

If Azure CLI is not available, the app runs in demo mode with sample data to showcase all features.

## Requirements

- Python 3.8+
- Azure CLI (optional)
- TinyLlama model (~600MB) 