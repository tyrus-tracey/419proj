import sys
import subprocess
from formatters import *
from printhelper import printJudgementTask, printSentimentJudgement, printAttackJudgement

def run_model_task(target_model: str, task: str) -> str:
    output = subprocess.run(
        ["ollama", "run", target_model],
        input=task,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace"
    )
    if output.returncode != 0:
        sys.stderr.write(output.stderr)
        return "Sorry I didn't get that, could you say that again?\n"

    return output.stdout.strip()

# Given a conversation (i.e. multiple turns of prompt+response), elicit a new response 
def ollama_send_conversation(target_model: str, prompt: str) -> str:    
    response = run_model_task(target_model, prompt)
    return response

def ollama_evaluate_response_sentiment(prompt: str, response: str, DEBUG_MODE: bool) -> bool:
    task = format_to_response_sentiment_task(prompt, response)
    if DEBUG_MODE:
        printJudgementTask(task)
    
    judgement = run_model_task("mistral", task)
    json_judgement = json.loads(judgement)
    
    if DEBUG_MODE:
        printSentimentJudgement(json_judgement)

    return json_judgement["response sentiment"] == "POSITIVE"

def ollama_evaluate_manual_attack_success(conversation: list[str], LOG_OUTPUT: bool, DEBUG_MODE: bool) -> bool:
    task = format_to_attack_judgement_task(conversation)
    if DEBUG_MODE:
        printJudgementTask(task)

    judgement = run_model_task("mistral", task)
    json_judgement = json.loads(judgement)
    
    printAttackJudgement(json_judgement)

    if LOG_OUTPUT:
        logfile = open("log.txt", "w")
        logfile.write(f"EVALUATION TASK:\n{task}")
        if json_judgement["successful attack"]:
            logfile.write(f"SCENARIO JUDGEMENT: ATTACK SUCCEEDED\n")
        else:
            logfile.write(f"SCENARIO JUDGEMENT: ATTACK FAILED\n")
        logfile.write(f"REASON: \n{json_judgement["reason"]}")

    return json_judgement["successful attack"]


def ollama_evaluate_auto_attack_success(conversation: list[str], harmful_query: str, LOG_OUTPUT: bool, DEBUG_MODE: bool) -> bool:
    task = format_to_attack_judgement_task(conversation)
    if DEBUG_MODE:
        printJudgementTask(task)

    judgement = run_model_task("mistral", task)
    json_judgement = json.loads(judgement)
    
    printAttackJudgement(json_judgement)

    if LOG_OUTPUT:
        logfile = open("log.txt", "w")
        logfile.write(f"Harmful query: {harmful_query}\n")
        logfile.write(f"EVALUATION TASK:\n{task}")
        if json_judgement["successful attack"]:
            logfile.write(f"SCENARIO JUDGEMENT: ATTACK SUCCEEDED")
        else:
            logfile.write(f"SCENARIO JUDGEMENT: ATTACK FAILED")
        logfile.write(f"\nREASON: \n{json_judgement["reason"]}")

    return json_judgement["successful attack"]

def ollama_generate_opener(attacker_model, harmful_query: str) -> str:
    task = format_to_generate_opener_task(harmful_query)

    opener = run_model_task(attacker_model, task)
    return opener

def ollama_generate_next_line(attacker_model, harmful_query: str, conversation: list[str], round_number: int, jailbreak_indicator: bool, DEBUG_MODE: bool) -> str:
    task = format_to_generate_next_line_task(harmful_query, conversation, round_number, jailbreak_indicator)

    if DEBUG_MODE:
        print(task)

    next_line = run_model_task(attacker_model, task)
    return next_line