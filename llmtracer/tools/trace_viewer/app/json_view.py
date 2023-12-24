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

"""
https://monojack.github.io/react-object-view/

import { ObjectView } from 'react-object-view'

const options = {
  hideDataTypes: false,
  hideObjectSize: false,
  hidePreviews: false
}
const palette = {}
const styles = {}
const data = {/** copy this from the `Data` tab */}

function App() {
  return (
    <ObjectView
      data={data}
      options={options}
      styles={styles}
      palette={palette}
    />
  )
}
"""


class JsonView(rx.Component):
    if False:
        library = "react-object-view"
        tag = "ObjectView"
    elif True:
        library = "react-json-view-lite"
        tag = "JsonView"
    data: rx.Var[object]
    # options: pc.Var[dict] = {}
    # styles: pc.Var[dict] = {}
    # palette: pc.Var[dict] = {}

    # @classmethod
    # def get_controlled_triggers(cls) -> dict[str, pc.Var]:
    #     return {"on_change": pc.EVENT_ARG}


json_view = JsonView.create
