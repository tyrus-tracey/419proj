from conversation import *
from judge import ollama_evaluate_attack_success, ollama_evaluate_response_sentiment
from printhelper import *

def EndOfScenario(script_node: json) -> bool:
    return script_node["branches"] == {}

# Runs each attack scenario from script, terminates early if a scenario
#   successfully jailbreaks the target model.
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