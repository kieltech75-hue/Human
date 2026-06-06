Publishing the Human Language VS Code Extension
===============================================

This guide covers steps to publish the `Human Language` VS Code extension to the Visual Studio Marketplace and how to automate publishing with GitHub Actions.

Prerequisites
- A GitHub repository containing the extension (this repo).
- `package.json` with `name`, `publisher`, `version`, and `contributes` fields set correctly.
- A publisher account on the Visual Studio Marketplace (publisher name must match `package.json.publisher`).
- A Personal Access Token (PAT) for publishing; store it as a repository secret named `VSCE_TOKEN`.

Create a publisher
1. Open the Visual Studio Marketplace publisher management page: https://marketplace.visualstudio.com/manage
2. Create a new publisher and note the publisher ID.
3. Update `package.json` `publisher` field with the publisher ID if needed.

Create a Personal Access Token (PAT)
- Create a PAT suitable for `vsce` publishing. You can create this from the Azure DevOps/Visual Studio Marketplace account settings. Copy the token once created.
- In your GitHub repository settings → Secrets and variables → Actions, add a new secret named `VSCE_TOKEN` with the token value.

Local publish steps
1. Install the `vsce` tool:

```bash
npm install -g vsce
```

2. Build/package the extension:

```bash
vsce package
# produces human-language-<version>.vsix
```

3. Publish (use PAT):

```bash
vsce publish --pat $VSCE_TOKEN
```

Automated publishing (GitHub Actions)
- This repository includes a workflow at `.github/workflows/publish.yml` that runs on new releases and via manual dispatch. It:
  - Installs `vsce`.
  - Packages the extension.
  - Publishes using the `VSCE_TOKEN` secret.
  - Uploads the generated `.vsix` as a workflow artifact.

Notes & best practices
- Use semantic versioning in `package.json` and create a GitHub release (tag) to trigger publishing.
- Test your `.vsix` locally before publishing: `code --install-extension human-language-0.1.0.vsix`.
- Add screenshots and a good `README.md` describing features for the Marketplace listing.
- Consider adding CI jobs to run extension tests (if you add integration tests) before publishing.

Troubleshooting
- `vsce publish` errors: ensure the `VSCE_TOKEN` is valid, the publisher matches `package.json`, and the token has appropriate scopes.
- If `vsce` reports an existing version, bump `package.json.version` and create a new release.

If you'd like, I can:
- Add a pre-release workflow that builds and uploads a `.vsix` artifact for every PR.
- Add automated screenshots generation or a Marketplace metadata workflow.

Release labels (used by `release-please`)
---------------------------------------

This repository uses `release-please` to create label-driven releases. Add one of the following labels to a PR (or to the merge commit) to control the release bump:

- `release: major` — bumps the major version (breaking changes)
- `release: minor` — bumps the minor version (backwards-compatible features)
- `release: patch` — bumps the patch version (bug fixes)

Usage example:

1. Add the `release: minor` label to a PR that introduces a new feature.
2. Merge the PR to `main`.
3. `release-please` will open a release PR or create a release depending on configuration. Review and merge the release PR to publish.

If you prefer commit-message or labelless semantic releases, this repo now supports `semantic-release` instead of label-based `release-please`.

semantic-release notes
----------------------

- `semantic-release` determines the next version and creates a GitHub release based on commit messages following the Conventional Commits (Angular) format.
- Common commit prefixes:
  - `feat:` — new feature (minor bump)
  - `fix:` — bug fix (patch bump)
  - `perf:` — performance improvement (patch/minor depending on config)
  - `BREAKING CHANGE: ` in the commit body or `!` after the type — major bump

Usage:

1. Use Conventional Commits for PRs/commits. Example: `feat: add new parser option`.
2. Merge to `main` — the `.github/workflows/semantic-release.yml` workflow runs and will create a GitHub release if commits indicate a version bump.
3. The existing publish workflow (`.github/workflows/publish.yml`) will run on the created release and publish the VSIX to the Marketplace (requires `VSCE_TOKEN`).

If you'd rather keep label-based releases, I can revert to `release-please` instead.
