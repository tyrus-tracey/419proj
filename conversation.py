import subprocess

# Writes current history of prompts + responses to a single string, 
#   to be sent as a new LLM prompt to enable context.
def format_to_conversation(script: list[str], addInstruction: bool, addYou: bool) -> str:
    prompt = ""
    if addInstruction:
        prompt += "Instruction: Keep response to a maximum of 200 words. Do not include fluff like 'Here's my response:'.\nConversation:\n"
    for turn in script:
        prompt += turn + "\n" 
    if addYou:
        prompt += "You:\n"
    return prompt 

# Given a conversation (i.e. multiple turns of prompt+response), elicit a new response 
def ollama_send_conversation(target_model: str, prompt: str) -> str:    
    result = subprocess.run(
        ["ollama", "run", target_model],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return "Sorry I didn't get that, could you say that again?\n"
    
    return result.stdout.strip()