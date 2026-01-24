# Workflows Configuration

This directory contains GitHub Actions workflows for the repository.

## Release Workflow Setup

The `release.yml` workflow handles automated semantic releases. Due to branch protection rules, it requires additional configuration:

### Required Secrets

#### PAT_TOKEN (Required for branch protection bypass)

To enable the release workflow to push to protected branches, you need to create a Personal Access Token:

1. **Create a Fine-grained Personal Access Token:**
   - Go to https://github.com/settings/tokens?type=beta
   - Click "Generate new token"
   - Configure:
     - Token name: `gsp-py-semantic-release` (or similar)
     - Repository access: "Only select repositories" → Select `jacksonpradolima/gsp-py`
     - Repository permissions:
       - Contents: Read and write
       - Metadata: Read-only
       - Workflows: Read and write
     - Enable "Allow bypassing branch protection" if available

2. **Add the token to repository secrets:**
   - Go to repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PAT_TOKEN`
   - Value: Paste the generated token

#### GPG Signing (Optional, required if branch protection enforces signature verification)

If your branch protection rules require verified signatures:

1. **Generate a GPG key:**
   ```bash
   gpg --quick-gen-key "github-actions[bot] <github-actions[bot]@users.noreply.github.com>" rsa4096
   ```

2. **Export the private key:**
   ```bash
   # List keys to get the KEY_ID
   gpg --list-secret-keys --keyid-format=long
   
   # Export the private key
   gpg --armor --export-secret-key YOUR_KEY_ID
   ```

3. **Add secrets to repository:**
   - `GPG_PRIVATE_KEY`: The exported private key (including the BEGIN/END lines)
   - `GPG_PASSPHRASE`: The passphrase (if you set one during creation)

4. **Upload the public key to GitHub:**
   ```bash
   gpg --armor --export YOUR_KEY_ID
   ```
   - Go to https://github.com/settings/keys
   - Click "New GPG key"
   - Paste the public key

### Alternative: GitHub App

Instead of a PAT, you can use a GitHub App with the necessary permissions. This is often more secure and manageable for organizations.

1. Create a GitHub App with the required permissions
2. Install the app on the repository
3. Use an action like `tibdex/github-app-token` to generate a token in the workflow
4. Update the workflow to use the generated token

## Workflow Details

For more information about the semantic release workflow, see [docs/RELEASE_MANAGEMENT.md](../../docs/RELEASE_MANAGEMENT.md).
