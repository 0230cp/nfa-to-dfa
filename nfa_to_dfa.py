#.txt 파일 불러오는 함수 ----------------------------------------------------------------------------------
# 과제 게시물 예제로 출력 test 해봤는데 q005에 대한 처리가 아예 안됨.
# delta_func에만 등장할 수 있는 state에 대한 처리 로직 추가 해야함.

def load_txt(filepath):
    delta_flag = False
    nfa_states = set()
    nfa_terminal_set = set() 
    nfa_delta_func = {} 
    nfa_start_state = ""
    nfa_final_states = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("StateSet"):
                raw = line.split("=")[1].strip().strip("{}")
                nfa_states = set(s.strip() for s in raw.split(","))
            elif line.startswith("TerminalSet"):
                raw = line.split("=")[1].strip().strip("{}")
                nfa_terminal_set = set(s.strip() for s in raw.split(","))
            elif line.startswith("DeltaFunctions"):
                delta_flag = True
                continue;
            elif delta_flag:
                if line.startswith("}"):
                    delta_flag = False
                    continue;
                else :
                    left, right = line.split("=")
                    left = left.strip()[1:-1]
                    state, symbol = [s.strip() for s in left.split(",")]
                    targets = set(s.strip() for s in right.strip()[1:-1].split(","))
                    nfa_delta_func[(state, symbol)] = targets;
                    nfa_states.add(state)
                    nfa_states.update(targets)
            elif line.startswith("StartState"):
                nfa_start_state = line.split("=")[1].strip()
            elif line.startswith("FinalStateSet"):
                raw = line.split("=")[1].strip().strip("{}")
                nfa_final_states = set(s.strip() for s in raw.split(","))
    return nfa_states, nfa_terminal_set, nfa_delta_func, nfa_start_state, nfa_final_states


# 이동 함수 구현 ----------------------------------------------------------------------------------
# 1. 기존 nfa_state 기반
# 2. 상태 전이로 넘어가는 state
# 3. ε타고 넘어가는 state
# @@주의할 점은 넘어가는 과정이 한 단계에서 마무리 되면 안됨@@
# DFA state을 먼저 구하려고 알고리즘을 생각했으나 state를 시작하는 start state가 필요함. 
# 해당 단계에 필요한 상태 전이 함수 2가지 case 구현 우선

# 1. symbol 타고 넘어가는 state 구하는 함수
def move(states, symbol, nfa_delta_func):
    result = set()
    for state in states:
        if(state, symbol) in nfa_delta_func:
            result.update(nfa_delta_func[(state, symbol)])
    return result


# 2. ε 타고 넘어가는 state 구하는 함수
def epsilon_move(states, nfa_delta_func):
    epsilon_move_states = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        for(s, symbol), target in nfa_delta_func.items():
            if s == state and symbol == 'ε':
                for t in target:
                    if t not in epsilon_move_states:
                        epsilon_move_states.add(t)
                        stack.append(t)
    return epsilon_move_states

# DFA start states 구하기 ---------------------------------------------------------------------------
# 기존 start state가 ε으로 이동할 수 있는 경우가 있기에 항상 check 필요
# start state는 문장인데 그냥 받으려고 하니 오류가 계속 났음. {}로 감싸서 str을 set으로 받아줘야함
def get_dfa_start_states(nfa_start_state, nfa_delta_func):
    dfa_start_states = set(epsilon_move({nfa_start_state}, nfa_delta_func))
    return dfa_start_states

# DFA state 구하기 ----------------------------------------------------------------------------------
def get_dfa_state(nfa_start_state, nfa_terminal_set, nfa_delta_func):
    from collections import deque 
    #queue없이 구하기가 너무 어려웠음 특히, symbol을 보면서 넘어가야하는데 for문으로 terminal을 하나씩 탐색하면서 구현해보려 했으나 오류가 많이 나 GPT에게 구조 추천을 받았음

    dfa_states = set()
    start = frozenset(get_dfa_start_states(nfa_start_state, nfa_delta_func))
    queue = deque([start])
    dfa_states.add(start)

    while queue:
        current = queue.popleft()
        for symbol in nfa_terminal_set:
            next_nfa = move(current, symbol, nfa_delta_func)
            next_epsilon = frozenset(epsilon_move(next_nfa, nfa_delta_func))

            if next_epsilon not in dfa_states:
                dfa_states.add(next_epsilon)
                queue.append(next_epsilon)

    return dfa_states


# DFA, terminal symbol set ----------------------------------------------------------------------------------
# 이건 달라지지 않는 값
def get_dfa_terminal_set(nfa_terminal_set):
    return nfa_terminal_set

# DFA, delta' funtions 구하기 ----------------------------------------------------------------------------------
# 우선 이 부분은 time
# 머릿속으로는 기존 delta func들 담고 dict((state), (terminal)) : state) 이런 식으로 담으면 될 거 같은데 
# 저 state 부분에 또 tuple이 담기거나 set이 담겨야 하는 상황이 발생할거 같음 그게 가능한지와 어떻게 담아낼건지
# 효율적으로 담으려면 손으로 표 그리는 것처럼 한 state 만나는 symbol 확인하고 있으면 value에 넣고 다음 state 만나고 확인하고 넣고
def get_dfa_delta_func(dfa_states, nfa_terminal_set, nfa_delta_func):
    dfa_delta_func = {}

    for dfa_state in dfa_states:
        for symbol in nfa_terminal_set:
            temp_state = move(dfa_state, symbol, nfa_delta_func)
            next_state = frozenset(epsilon_move(temp_state, nfa_delta_func))
            dfa_delta_func[(dfa_state, symbol)] = next_state
    return dfa_delta_func

# DFA final_state ----------------------------------------------------------------------------------
# 여기서도 오류가 엄청 났는데
# frozenset과 일반 set을 비교하려다 보니 문제가 생겼음
# for문이랑 in 연산자를 쓰려다보니 복잡했는데 그냥 &로 교집합 구하는 방식이 가장 적절한듯함.
# 과제 게시물 예제처럼 final_state가 어느 state에서도 접근할 수 없는 경우
# 위키독스와 논문 2편을 봤을 때 과제 게시물에 해당하는 case를 이렇다하게 명확하게 제시해주는 경우가 없었음.
# 근데 논리상 delta_func를 통해 도달하는 state 중 final_state를 하나라도 포함하는 state라고 했을 때
# 과제 예제와 같은 경우는 determinstic이라는 말에 맞게 final_state를 없다?라고 표현하는게 맞다고 느껴졌음. 그래서 구현 시 그걸 반영 
def get_dfa_final_state(dfa_states, nfa_final_state):
    dfa_final_states = set()
    for state in dfa_states:
        if state & nfa_final_state:
            dfa_final_states.add(state)
    return dfa_final_states

def test_dfa_all(filepath):
    print(f"\n📄 Loading NFA from file: {filepath}")
    nfa_states, nfa_terminal_set, nfa_delta_func, nfa_start_state, nfa_final_states = load_txt(filepath)

    print("\n✅ NFA 구성 요소:")
    print("States:", sorted(nfa_states))
    print("Terminals:", sorted(nfa_terminal_set))
    print("Start state:", nfa_start_state)
    print("Final states:", sorted(nfa_final_states))
    print("Delta function:")
    for (s, a), t in nfa_delta_func.items():
        print(f"  δ({s}, '{a}') = {sorted(t)}")

    print("\n🔁 DFA 변환 중...")
    dfa_states = get_dfa_state(nfa_start_state, nfa_terminal_set, nfa_delta_func)
    dfa_start = get_dfa_start_states(nfa_start_state, nfa_delta_func)
    dfa_final = get_dfa_final_state(dfa_states, nfa_final_states)
    dfa_delta_func = get_dfa_delta_func(dfa_states, nfa_terminal_set, nfa_delta_func)

    print("\n✅ DFA 구성 요소:")
    print("Start state:", sorted(dfa_start))
    print("States:")
    for s in dfa_states:
        print(" ", sorted(s))
    print("Final states:")
    for s in dfa_final:
        print(" ", sorted(s))

    print("\n✅ DFA Delta Function:")
    for (s, a), t in dfa_delta_func.items():
        print(f"  δ({sorted(s)}, '{a}') → {sorted(t)}")

test_dfa_all("test.txt")
