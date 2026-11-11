"""Student assignment: complete an explicit transition table.

All mappings are a proposed course model. The engine already implements sensor
guards, bounded movement/RGB and output scheduling. Edit only this function.
Return a state name, or None when the event has no transition.
"""


def transition(current_state: str, event: str) -> str | None:
    # 1. Global Priority Guards (fault, near, clear)
    if event == "fault":
        return "normal"
    if event == "near":
        return "afraid"
    if event == "clear":
        return "normal"

    # 2. Afraid State Guard: ถ้าอยู่ใน afraid แต่ไม่ใช่ clear/fault ให้คืน None เพื่อคง state เดิม
    if current_state == "afraid":
        return None

    # 3. Interactive State Transitions
    if event == "touch":
        return "happy"
    if event in ("button", "approach"):
        return "interested"

    # 4. Inactivity & Timeout Transitions
    if event == "timeout":
        if current_state in ("interested", "happy"):
            return "normal"
        return None

    if event == "idle":
        if current_state == "normal":
            return "sleepy"
        return None

    return None