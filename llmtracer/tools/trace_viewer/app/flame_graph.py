import pynecone as pc
from pydantic import BaseModel, Field


class FlameGraphNode(BaseModel):
    name: str
    value: int
    children: list["FlameGraphNode"]
    color: str | None = None
    backgroundColor: str | None = Field(None, alias="background_color")
    tooltip: str | None = None
    id: str | None = None


class FlameGraph(pc.Component):
    library = "react-flame-graph"
    tag = "FlameGraph"

    data: pc.Var[dict]
    height: pc.Var[int]
    width: pc.Var[int]

    @classmethod
    def get_controlled_triggers(cls) -> dict[str, pc.Var]:
        return {"on_change": pc.EVENT_ARG}


flame_graph = FlameGraph.create
