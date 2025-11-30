import subprocess
import sys
from judge import ollama_evaluate_attack_success, ollama_evaluate_response_sentiment
from printhelper import *

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

def EndOfScenario(script_node: json) -> bool:
    return script_node["branches"] == {}

def start_attack(target_model, script: json, DEBUG_MODE: bool):
    for scenario_num, scenario in enumerate(script["scenarios"]):
        history = []
        line_num = 0
        printScenarioHeader(scenario_num+1, scenario["name"])
        script_node_id = scenario["start_node"]

        while script_node_id:
            script_node = scenario["nodes"][script_node_id]
            line = script_node["line"]
            history.append("USER:\n" + line)
            conversation = format_to_conversation(history, addInstruction=True, addYou=True)

            if DEBUG_MODE:
                printConversation(conversation)
            else:
                printLine(line, line_num)

            response = ollama_send_conversation(target_model, conversation)
            history.append("LLM:\n" + response)
            printResponse(response, line_num)

            conversation = format_to_conversation(history, addInstruction=False, addYou=False)

            if EndOfScenario(script_node):
                break;
            if ollama_evaluate_response_sentiment(line, response, DEBUG_MODE):
                script_node_id = script_node["branches"]["POSITIVE"]
                printSuccess(line_num)
            else:
                script_node_id = script_node["branches"]["NEGATIVE"]
                printFailure(line_num)
            line_num += 1

        # Conversation concluded, evaluate whether attack succeeded.
        conversation_log = format_to_conversation(script, addInstruction=False, addYou=False)

        if ollama_evaluate_attack_success(conversation_log, DEBUG_MODE):
            print("SCENARIO EVALUTION: Success")
            print("Ending attack.")
            break;
        else:
            print("SCENARIO EVALUTION: Fail")
    
        
if __name__ == "__main__":
    colorama.init()

    DEBUG_MODE = False
    target_model = "llama3"
    n_attempts = 1

    scriptfile = open("scenarioscripts.json", "r")
    json_script = json.load(scriptfile)

    start_attack(target_model, json_script, DEBUG_MODE)