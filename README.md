<p align="center"><img src=./res/logo.png></p>

# scroller
[![Test (CI)](https://github.com/robert-clayton/scroller/actions/workflows/test.yml/badge.svg)](https://github.com/robert-clayton/scroller/actions/workflows/test.yml)

A simple application that scrolls through a folder's images.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Support](#support)
- [Contribution](#contribution)
- [License](#license)

## Features
- Scroll through images in a folder
- Control scroll speed with scroll wheel
- Add/Remove columns to scroll view
- Save hovered image to `~/pictures/saved` via middle-click

## Prerequisites
- Python >=3.9, <3.12
- PySide6

## Installation
Navigate to the releases page found [here](https://github.com/robert-clayton/scroller/releases) and download the latest release. Extract the contents of the `scroller-v*.zip` archive and run `scroller.exe` found within.

## Usage
To run the application, execute the following command:
```sh
make run scroller
```

## Development
Clone the repository and run the following commands to install dependencies:
```sh
git clone https://github.com/robert-clayton/scroller.git
cd scroller && make install
```

## Testing
To run the tests, execute the following command:
```sh
make test
```

## Support
Please [open an issue](https://github.com/robert-clayton/scroller/issues/new) for support.

## Contribution
We appreciate any contribution, from fixing a grammar mistake in a comment to implementing complex algorithms. Please read this section if you are contributing your work.

Your contribution will be tested by our automated testing on GitHub Actions to save time and mental energy. After you have submitted your pull request, you should see the GitHub Actions tests start to run at the bottom of your submission page. If those tests fail, then click on the details button try to read through the GitHub Actions output to understand the failure. If you do not understand, please leave a comment on your submission page and a community member will try to help.

Please help us keep our issue list small by adding fixes: #{$ISSUE_NO} to the commit message of pull requests that resolve open issues. GitHub will use this tag to auto-close the issue when the PR is merged.

## Keybinds
- `Ctrl-O` - set folder to view
- `Scrollwheel` - increase/decrease scroll speed
- `Ctrl-Scrollwheel` - add/remove column to scroll view
- `Middle Mouse Button` - saves the hovered image to `~/pictures/saved` (on windows)

## License
This project is licensed under the [MIT](LICENSE) License. 