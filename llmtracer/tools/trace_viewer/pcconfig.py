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
import os
import subprocess
import sys

import pynecone.pc as cli
from app.pcconfig import *  # noqa: F401, F403


def main():
    """This is the entry point for the CLI."""
    # Add the chatplayground directory to PYTHONPATH and change directories into it
    os.environ["PYTHONPATH"] = os.path.abspath(os.path.dirname(__file__))
    os.chdir(os.path.dirname(__file__))
    print(os.getcwd())
    subprocess.run([sys.executable, "-m", "pynecone.pc", "init"], check=True, cwd=os.getcwd())
    cli.main(["run"] + sys.argv[1:])


if __name__ == "__main__":
    main()
