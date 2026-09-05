import json
from pathlib import Path

from autonomy_evals.scenarios.v02 import expand_candidate
from autonomy_evals.schemas.scenario import Scenario


def load(paths: list[str]) -> list[Scenario]:
    result = []
    for name in paths:
        path = Path(name)
        for index, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                if "scenario_id" in raw:
                    result.append(Scenario.model_validate(raw))
                elif raw.get("status") == "candidate" and "scenario_family" in raw:
                    result.extend(expand_candidate(raw))
                else:
                    raise ValueError("record is neither a Scenario nor a v0.2 candidate record")
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"{path}:{index}: {exc}") from exc
    if not result:
        raise ValueError("empty dataset")
    return result
