#  LLM Tracer
#  Copyright (c) 2023. Andreas Kirsch
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pynecone as pc

config = pc.Config(
    app_name="app",
    db_url="sqlite:///pynecone.db",
    port=3333,
    backend_port=8333,
    api_url="http://localhost:8333",
    env=pc.Env.DEV,
    frontend_packages=[
        "react-flame-graph",
        "react-object-view",
        "react-json-view-lite",
    ],
)
