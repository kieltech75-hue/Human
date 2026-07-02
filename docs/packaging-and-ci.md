# Packaging and CI for Human apps

## Release assets for v0.1.6

The latest release assets are published at [GitHub Releases v0.1.6](https://github.com/kieltech75-hue/Human/releases/tag/v0.1.6).

Available downloads:
- Linux: [linux-human-language](https://github.com/kieltech75-hue/Human/releases/download/v0.1.6/linux-human-language)
- macOS: [macos-human-language](https://github.com/kieltech75-hue/Human/releases/download/v0.1.6/macos-human-language)
- Windows installer helper: [windows-human-language-installer.bat](https://github.com/kieltech75-hue/Human/releases/download/v0.1.6/windows-human-language-installer.bat)
- Windows executable: [windows-human-language-setup.exe](https://github.com/kieltech75-hue/Human/releases/download/v0.1.6/windows-human-language-setup.exe)

## Build native executables for release

The release workflow uses the helper script at [scripts/build_native_release_asset.py](../scripts/build_native_release_asset.py) to build a platform-specific executable and the Windows helper script at [scripts/build_windows_installer.ps1](../scripts/build_windows_installer.ps1) to prepare the Windows installer asset.

```bash
python scripts/build_native_release_asset.py --platform windows --output-dir dist/windows --name windows-human-language-setup.exe
python scripts/build_native_release_asset.py --platform linux --output-dir dist/linux --name linux-human-language
python scripts/build_native_release_asset.py --platform macos --output-dir dist/macos --name macos-human-language
```

## Build a native executable from source

```bash
human --package-native examples/hello_world.hm --dist dist/ --bundle-python --name human-app
```

This produces a self-contained executable in the `dist/` folder.

## CI and publishing workflow

The repository now includes:
- a GitHub Actions release workflow for building and uploading binaries
- a PyPI publishing workflow for wheels
- placeholder deployment steps for OpenVSX and JetBrains Marketplace

These workflows are defined in [.github/workflows/release.yml](../.github/workflows/release.yml) and [.github/workflows/publish-pypi.yml](../.github/workflows/publish-pypi.yml).

## Docker image option

The repository also includes a Dockerfile for containerized deployment.

```bash
docker build -t human-app .
docker run -p 8080:8080 human-app
```
