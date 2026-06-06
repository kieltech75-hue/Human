# Human Language VS Code Extension

This extension provides syntax highlighting, basic language configuration, and icon support for the Human programming language (.hm files).

## Features

- TextMate grammar for tokens: comments, strings, numbers, booleans, keywords, builtins, functions, classes, and parameters
- Language configuration: comments, brackets, auto-closing pairs, and folding
- Custom file icon (human-icon.png)

## How to test locally

1. Open this repository folder in VS Code.
2. Press `F5` to launch an Extension Development Host window.
3. In the new window, open or create a file with the `.hm` extension (for example `examples/syntax_highlight_test.hm`).
4. The Human language should be available from the language selector and syntax highlighting should be active.

## Screenshots

Add screenshots to the `images/` folder and reference them here. Example markdown placeholder:

![Highlighting sample](images/highlight-sample.png)

## Packaging and publishing

To package and publish the extension to the Visual Studio Marketplace, use `vsce`:

```bash
npm install -g vsce
vsce package
vsce publish
```

You will need to create a publisher in the Visual Studio Marketplace and use a Personal Access Token for publishing.

## License

MIT — see the LICENSE file.
