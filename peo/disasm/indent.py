from typing import List


space = []


def organize(msgs: List[List[str]]) -> List[List[str]]:
    max_size = max(
        [len(msgs[i][1]) for i in range(len(msgs)) if len(msgs[i]) >= 2]
    )

    for i in range(len(msgs)):
        if len(msgs[i]) >= 2:
            l = max_size - len(msgs[i][1])
            msgs[i][1] = msgs[i][1] + " " * l

        elif len(msgs[i]) == 1:
            if "<" in msgs[i][0]:
                msg = msgs[i][0].split(" ")
                msgs[i][0] = msg[1]

    return msgs


def indent(arrows: List[str], msgs: List[List[str]]):
    global space
    max_size = max(len(arrow) for arrow in arrows)
    for i in range(len(msgs)):
        if len(msgs[i]) == 1:
            l = max_size - len(arrows[i]) - 2
        else:
            l = max_size - len(arrows[i])
        space.append(l)


def combine(arrows: List[str], msgs: List[List[str]]) -> List[List[str]]:
    for i in range(len(msgs)):
        msgs[i][0] = " " * space[i] + arrows[i] + " " + msgs[i][0]

    return msgs
