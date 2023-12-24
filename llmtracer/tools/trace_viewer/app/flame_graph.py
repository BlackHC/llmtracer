#  LLM Tracer
#  Copyright (c) 2023. Andreas Kirsch
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import reflex as rx
from pydantic import BaseModel, Field


class FlameGraphNode(BaseModel):
    name: str
    value: int
    children: list["FlameGraphNode"]
    color: str | None = None
    backgroundColor: str | None = Field(None, alias="background_color")
    tooltip: str | None = None
    id: str | None = None


class FlameGraph(rx.Component):
    library = "react-flame-graph"
    tag = "FlameGraph"

    data: rx.Var[dict]
    height: rx.Var[int]
    width: rx.Var[int]

    @classmethod
    def get_controlled_triggers(cls) -> dict[str, rx.Var]:
        return {"on_change": rx.EVENT_ARG}


flame_graph = FlameGraph.create
