import pynecone as pc

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


class JsonView(pc.Component):
    if False:
        library = "react-object-view"
        tag = "ObjectView"
    elif True:
        library = "react-json-view-lite"
        tag = "JsonView"
    data: pc.Var[object]
    # options: pc.Var[dict] = {}
    # styles: pc.Var[dict] = {}
    # palette: pc.Var[dict] = {}

    # @classmethod
    # def get_controlled_triggers(cls) -> dict[str, pc.Var]:
    #     return {"on_change": pc.EVENT_ARG}


json_view = JsonView.create
