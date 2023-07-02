# LLMTracer

[![Twitter Follow](https://img.shields.io/twitter/follow/blackhc?style=social)](https://twitter.com/intent/follow?screen_name=blackhc)
[![pypi](https://img.shields.io/pypi/v/llmtracer.svg)](https://pypi.org/project/llmtracer/)
[![python](https://img.shields.io/pypi/pyversions/llmtracer.svg)](https://pypi.org/project/llmtracer/)
[![Build Status](https://github.com/blackhc/llmtracer/actions/workflows/dev.yml/badge.svg)](https://github.com/blackhc/llmtracer/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/blackhc/llmtracer/branch/main/graphs/badge.svg)](https://codecov.io/github/blackhc/llmtracer)
![License](https://img.shields.io/github/license/blackhc/llmtracer)

A simple (opinionated) library to trace calls to an LLM model (and more) with some batteries included:

* FlameCharts!
* JSON output;
* interactive SVG output;
* WandB integration;
* PyneCone app to stream the output to a web browser at runtime and explore saved JSON files

## Motivation

WandB only supports showing finished traces but I wanted to be able to view them in real-time (at finer granularity).

Further, I want to make it easier to explore nested and complex calls and display properties of the calls.

## Installation

### Node.JS

To install Chat Playground, first, make sure you have Node.js installed. You can use `conda` to install Node.js as follows:

```
conda install -c conda-forge nodejs
```

Or, to install a specific version of Node.js (this one worked for me on my MacBook---so this will not work on Linux):

```
conda install -c conda-forge nodejs=18.15.0=h26a3f6d_0
```

### Trace Viewer

Once Node.js is installed, you can install Chat Playground using `pip` or `pipx` (if you have nodejs available in your base environment):

```
pipx install llmtracer
```

### OpenAI Key :key:

Ensure that your OpenAI key is set in an OPENAI_API_KEY environment variable. You then can run the playground with

```
llmtracer
```

## Features

* Preview of possible alternative message threads as an exposee view.
* Preview of possible alternatives at the message level.
* Editing messages within a message thread without deleting everything below.
* Forking message threads (similar to the ChatGPT web app).
* Messages stored as JSON files in a local directory.
* Easy sync with cloud services like Dropbox or Google Drive.
* Real-time updates from the filesystem to the UI.
* Atomic changes of the stored messages.

## Screenshots

![./docs/app_interface.png](./docs/app_interface.png)

![./docs/message_alternatives.png](./docs/message_alternatives.png)

![./docs/thread_exposee.png](./docs/thread_exposee.png)

## Code & Layout

This project was written in ~25 hours using [Pynecone](https://pynecone.io/). The code is currently in one big Python file, which may benefit from refactoring into a package with multiple files. However, the code is mostly simple and it was quite productive to keep everything together.

There are a few issues with the current code (in part due to Pynecone's early stage of development):

- No tests currently.
- Calling event functions in State classes requires passing self, even though it shouldn't: `self.state_event_function(self)`.
- Issues with streaming events from the OpenAI request to the UI, requiring a hacky workaround for updates to propagate to the UI correctly.
- Known Pynecone issues, as mentioned in the code.

Despite these issues, the project came together very quickly with PyneCone and works quite well.

## Documentation

* License: GPL-3.0-only
* Source Code: <https://github.com/blackhc/llmtracer>
* PyPI Package: <https://pypi.org/project/llmtracer/>
* Official Documentation: <https://blackhc.github.io/llmtracer>

## Contributing

Bug fixes, feature requests, and pull requests are welcome! If you have any questions or suggestions, please open an issue on GitHub.

## License

LLMTracer is licensed under AGPL3.0. If you require a commercial license for any part of the project, please contact the author.

## Credits

This package was created using [PyneCone](https://pynecone.io/) with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.
