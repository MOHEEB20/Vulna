@echo off
echo 🚀 Vulna Model Switcher
echo Available models:
echo.

REM Show available Ollama models
ollama list

echo.
echo 🎯 Recommended for Penetration Testing:
echo 1. qwen2.5-coder:14b     (BEST - Code/Security focused, 14B params)
echo 2. deepseek-r1:14b       (GOOD - Reasoning focused, 14B params)  
echo 3. qwen2.5-coder:latest  (OK - Lighter version, 7B params)
echo 4. llama3-groq-tool-use:8b (OK - Tool specialized)
echo 5. llama3.2:latest       (POOR - Too small, 2B params)
echo.

set /p model_choice="Enter model name (or press Enter for qwen2.5-coder:14b): "

if "%model_choice%"=="" set model_choice=qwen2.5-coder:14b

echo.
echo 🔄 Setting model to: %model_choice%

REM Create or update .env file
if not exist .env (
    copy .env.example .env
    echo 📝 Created .env file from template
)

REM Update the model in .env file (Windows way)
powershell -Command "(Get-Content .env) -replace 'OLLAMA_MODEL=.*', 'OLLAMA_MODEL=%model_choice%' | Set-Content .env"

echo ✅ Model updated in .env file
echo.
echo 🎯 To apply changes:
echo 1. Restart Vulna: python -m backend.main
echo 2. The new model will be loaded automatically
echo.
echo 📊 Model Performance Comparison:
echo qwen2.5-coder:14b  → ⭐⭐⭐⭐⭐ (Best security analysis)
echo deepseek-r1:14b    → ⭐⭐⭐⭐⭐ (Best reasoning)
echo qwen2.5-coder:7b   → ⭐⭐⭐⭐   (Good, lighter)
echo llama3.2:latest    → ⭐⭐     (Basic, fast)
echo.
pause
