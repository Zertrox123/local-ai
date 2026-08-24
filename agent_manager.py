import subprocess
import time
import sys
from openai import OpenAI

ROUTER_ID = "mistralai/ministral-3-3b"
PYTHON_EXPERT_ID = "qwen/qwen3-coder-30b"
C_EXPERT_ID = "mistralai/devstral-small-2-2512"
GENERAL_ID = "qwen/qwen3-vl-8b"

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
chat_memory = []

def load_model(model_id, callback=None):
    msg = f"\nChargement du modèle : {model_id}...\n"
    print(msg)
    try:
        subprocess.run(["lms", "unload", "--all"], check=True, capture_output=True)
        subprocess.run(["lms", "load", model_id, "--gpu", "max"], check=True)
        time.sleep(1)
    except subprocess.CalledProcessError as e:
        error_msg = f"❌ Erreur chargement modèle : {e}\n"
        print(error_msg)
        if callback: callback(error_msg)

def get_router_decision(user_prompt):
    load_model(ROUTER_ID)
    system_prompt = """
    You are a Router Agent. Analyze the user request and output EXACTLY one of these categories:
    - PYTHON (for Python, Django, Pandas, scripting)
    - C_CPP (for C, C++, Rust, pointers, memory, embedded)
    - GENERAL (for creative writing, history, casual chat, facts)
    Return ONLY the category word.
    """
    try:
        response = client.chat.completions.create(
            model=ROUTER_ID,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.0
        )
        return response.choices[0].message.content.strip().upper()
    except Exception:
        return "GENERAL"

def run_expert(category, user_prompt, callback):
    global chat_memory
    if "PYTHON" in category:
        target_model = PYTHON_EXPERT_ID
        expert_name = "🐍 Qwen Coder 30B"
        sys_prompt = "You are a Python Expert. Write highly efficient code."
    elif "C_CPP" in category:
        target_model = C_EXPERT_ID
        expert_name = "⚙️ Devstral 24B"
        sys_prompt = "You are a C/C++ Expert. Focus on memory safety."
    else:
        target_model = GENERAL_ID
        expert_name = "🤖 Qwen General"
        sys_prompt = "You are a helpful assistant."
    load_model(target_model, callback)
    intro_msg = f"\n[{expert_name} prend la main...]\n"
    chat_memory.append({"role": "user", "content": user_prompt})
    full_messages = [{"role": "system", "content": sys_prompt}] + chat_memory
    stream = client.chat.completions.create(
        model=target_model,
        messages=full_messages,
        stream=True
    )
    full_response_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response_text += content
            if callback: callback(content)
    chat_memory.append({"role": "assistant", "content": full_response_text})

def initialization_chat(user_input, callback):
    try:
        callback(f"\nIA: ")
        decision = get_router_decision(user_input)
        run_expert(decision, user_input, callback)
    except Exception as e:
        callback(f"Erreur critique : {e}")