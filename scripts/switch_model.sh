#!/bin/bash
# Model Switcher Script for Vulna

echo "🚀 Vulna Model Switcher"
echo "Available models:"
echo ""

# Show available Ollama models
ollama list

echo ""
echo "🎯 Recommended for Penetration Testing:"
echo "1. qwen2.5-coder:14b     (BEST - Code/Security focused, 14B params)"  
echo "2. deepseek-r1:14b       (GOOD - Reasoning focused, 14B params)"
echo "3. qwen2.5-coder:latest  (OK - Lighter version, 7B params)"
echo "4. llama3-groq-tool-use:8b (OK - Tool specialized)"
echo "5. llama3.2:latest       (POOR - Too small, 2B params)"
echo ""

read -p "Enter model name (or press Enter for qwen2.5-coder:14b): " model_choice

if [ -z "$model_choice" ]; then
    model_choice="qwen2.5-coder:14b"
fi

echo ""
echo "🔄 Setting model to: $model_choice"

# Create or update .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file from template"
fi

# Update the model in .env file
if grep -q "OLLAMA_MODEL=" .env; then
    # Update existing line
    sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$model_choice/" .env
else
    # Add new line
    echo "OLLAMA_MODEL=$model_choice" >> .env
fi

echo "✅ Model updated in .env file"
echo ""
echo "🎯 To apply changes:"
echo "1. Restart Vulna: python -m backend.main"
echo "2. The new model will be loaded automatically"
echo ""
echo "📊 Model Performance Comparison:"
echo "qwen2.5-coder:14b  → ⭐⭐⭐⭐⭐ (Best security analysis)"
echo "deepseek-r1:14b    → ⭐⭐⭐⭐⭐ (Best reasoning)"  
echo "qwen2.5-coder:7b   → ⭐⭐⭐⭐   (Good, lighter)"
echo "llama3.2:latest    → ⭐⭐     (Basic, fast)"
