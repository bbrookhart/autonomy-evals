from inspect_ai.model import ChatMessageUser
from inspect_ai.solver import Generate, Solver, TaskState, solver

from autonomy_evals.conversations.state import render_turn
from autonomy_evals.schemas.scenario import Scenario


@solver
def autonomy_conversation() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        scenario = Scenario.model_validate(state.metadata["scenario"])
        # First user message is created in Sample; remaining turns append statefully.
        for index in range(1, len(scenario.conversation) + 1):
            if index > 1:
                state.messages.append(ChatMessageUser(content=render_turn(scenario, index)))
            state = await generate(state)
        return state

    return solve
