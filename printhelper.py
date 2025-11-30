import colorama
from colorama import Fore, Back, Style
import json

def printScenarioHeader(num: int, name: str):
    print(Fore.BLACK + f"==================== SCENARIO {num}: {name} ====================" + Style.RESET_ALL)

def printLine(line: str, line_num: int):
    print(Fore.BLUE + "line "  + str(line_num+1) + Style.RESET_ALL)
    print(line + "\n")

def printResponse(response: str, line_num: int):
    print(Fore.BLUE + "response " + str(line_num+1) + Style.RESET_ALL)
    print(response + "\n")

def printConversation(conversation: list[str]):
    print(Fore.GREEN + "### Conversation ###" + Style.RESET_ALL)
    print(conversation)
    print(Fore.GREEN + "### END Conversation ###" + Style.RESET_ALL)

def printJudgementTask(task: str):
    print(Fore.LIGHTWHITE_EX + Back.BLACK + "JUDGEMENT TASK:" + "\n" + task + Style.RESET_ALL)

def printSentimentJudgement(judgement: json):
    result: str
    if judgement["response sentiment"] == "POSITIVE":
        result = Fore.LIGHTGREEN_EX + "POSITIVE" + Style.RESET_ALL
    else:
        result = Fore.LIGHTRED_EX + "NEGATIVE"+ Style.RESET_ALL
    print(Fore.LIGHTWHITE_EX+ Back.BLACK + "RESPONSE SENTIMENT JUDGMENT: " + result + Style.RESET_ALL)
    print(Fore.LIGHTWHITE_EX+ Back.BLACK + "REASON:")
    print(Fore.LIGHTYELLOW_EX + judgement["reason"] + Style.RESET_ALL)

def printAttackJudgement(judgement: json):
    result: str
    if judgement["successful attack"]:
        result = Fore.LIGHTGREEN_EX + "ATTACK SUCCEEDED" + Style.RESET_ALL
    else:
        result = Fore.LIGHTRED_EX + "ATTACK FAILED"+ Style.RESET_ALL

    print(Fore.LIGHTWHITE_EX+ Back.BLACK + "ATTACK JUDGEMENT: " + result + Style.RESET_ALL)
    print(Fore.LIGHTWHITE_EX+ Back.BLACK + "REASON:")
    print(Fore.LIGHTYELLOW_EX + judgement["reason"] + Style.RESET_ALL)

def printSuccess(line: int):
    print(Fore.BLACK + Back.GREEN + f"LINE {line+1} SUCCEEDED" + Style.RESET_ALL + "\n")
    
def printFailure(line: int):
    print(Fore.BLACK + Back.RED + f"LINE {line+1} FAILED"+ Style.RESET_ALL + "\n")