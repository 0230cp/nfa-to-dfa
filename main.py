import os
from nfa_to_dfa import (
    load_txt,
    get_dfa_start_state,
    get_dfa_state,
    get_dfa_delta_func,
    get_dfa_final_state,
    del_inaccessible_states,
    hopcroft,
)


# console 청소
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_main_menu():
    print("----------(ε-)NFA → DFA → Reduced DFA 변환기--------")
    print("1. 콘솔에 출력")
    print("2. 파일로 출력 (output.txt)")
    print("0. 종료")
    print("-------------------------------------made by chan---")

def dfa_pipeline(filepath, to_file=False):
    try:
        # NFA 로드------------------------------
        nfa_states, nfa_terminal_set, nfa_delta_func, nfa_start_state, nfa_final_states = load_txt(filepath)

        # DFA 생성------------------------------
        dfa_start_state = get_dfa_start_state(nfa_start_state, nfa_delta_func)
        dfa_states = get_dfa_state(nfa_start_state, nfa_terminal_set, nfa_delta_func)
        dfa_delta_func = get_dfa_delta_func(dfa_states, nfa_terminal_set, nfa_delta_func)
        dfa_final_states = get_dfa_final_state(dfa_states, nfa_final_states)

        # Inaccessible 상태 제거(reduce DFA 파일 생성 -1)--------------------
        dfa_states, dfa_delta_func = del_inaccessible_states(dfa_states, frozenset(dfa_start_state), nfa_terminal_set, dfa_delta_func)

        # Reduced DFA 생성------------------------------
        reduced_states, reduced_start_state, reduced_final_states, reduced_delta_func, state_name_map = hopcroft(
            dfa_states, nfa_terminal_set, dfa_delta_func, frozenset(dfa_start_state), dfa_final_states
        )

        # 출력 준비----------------------------------------
        def format_delta(delta):
            return [f"  ({s}, {a}) = {t}" for (s, a), t in delta.items()]

        if to_file:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write("(ε-)NFA 구성 요소\n")
                f.write("StateSet = " + str(nfa_states) + "\n")
                f.write("TerminalSet = " + str(nfa_terminal_set) + "\n")
                f.write("StartState = " + str(nfa_start_state) + "\n")
                f.write("FinalStateSet = " + str(nfa_final_states) + "\n")
                f.write("DeltaFunctions = {\n")
                for (s, a), t in nfa_delta_func.items():
                    f.write(f"  ({s}, {a}) = {t}\n")
                f.write("}\n\n")

                f.write("DFA 구성 요소\n")
                f.write("StateSet = " + str(dfa_states) + "\n")
                f.write("TerminalSet = " + str(nfa_terminal_set) + "\n")
                f.write("StartState = " + str(frozenset(dfa_start_state)) + "\n")
                f.write("FinalStateSet = " + str(dfa_final_states) + "\n")
                f.write("DeltaFunctions = {\n")
                for line in format_delta(dfa_delta_func):
                    f.write(line + "\n")
                f.write("}\n\n")

                f.write("Reduced DFA 구성 요소\n")
                f.write("StateSet = " + str(reduced_states) + "\n")
                f.write("TerminalSet = " + str(nfa_terminal_set) + "\n")
                f.write("StartState = " + str(reduced_start_state) + "\n")
                f.write("FinalStateSet = " + str(reduced_final_states) + "\n")
                f.write("DeltaFunctions = {\n")
                for line in format_delta(reduced_delta_func):
                    f.write(line + "\n")
                f.write("}\n")
            print("'output.txt'가 다음 위치에 저장되었습니다.")
            print(os.path.abspath("output.txt"))

        else:
            print("(ε-)NFA 구성 요소")
            print("StateSet =", nfa_states)
            print("TerminalSet =", nfa_terminal_set)
            print("StartState =", nfa_start_state)
            print("FinalStateSet =", nfa_final_states)
            print("DeltaFunctions = {")
            for (s, a), t in nfa_delta_func.items():
                print(f"  ({s}, {a}) = {t}")
            print("}\n")

            print("DFA 구성 요소")
            print("StateSet =", dfa_states)
            print("TerminalSet =", nfa_terminal_set)
            print("StartState =", frozenset(dfa_start_state))
            print("FinalStateSet =", dfa_final_states)
            print("DeltaFunctions = {")
            for (s, a), t in dfa_delta_func.items():
                print(f"  ({s}, {a}) = {t}")
            print("}\n")

            print("Reduced DFA 구성 요소")
            print("StateSet =", reduced_states)
            print("TerminalSet =", nfa_terminal_set)
            print("StartState =", reduced_start_state)
            print("FinalStateSet =", reduced_final_states)
            print("DeltaFunctions = {")
            for (s, a), t in reduced_delta_func.items():
                print(f"  ({s}, {a}) = {t}")
            print("}")

    except Exception as e:
        print("오류 발생:", e)
    except PermissionError:
        print("'output.txt'가 열려 있어 덮어쓸 수 없습니다. 파일을 닫고 다시 시도하세요.")


def main():
    while True:
        clear_console()
        print_main_menu()
        choice = input("옵션을 선택하세요 (0-2): ").strip()

        if choice == "0":
            print("프로그램을 종료합니다.")
            break
        elif choice in ["1", "2"]:
            path = input("분석할 .txt 파일 경로를 입력하세요! \n(같은 폴더 내에 .txt파일이 존재할 경우 파일명만 적어주세요! e.g) test.txt)\n --> ").strip()
            if not os.path.exists(path):
                print("파일이 존재하지 않습니다.")
                input("Enter를 눌러 계속...")
                continue
            clear_console()
            dfa_pipeline(path, to_file=(choice == "2"))
            input("Enter를 눌러 메인 메뉴로 돌아가기...")
        else:
            print("옵션을 잘잘 확인해주세요.")
            input("Enter를 눌러 계속...")

if __name__ == "__main__":
    main()
