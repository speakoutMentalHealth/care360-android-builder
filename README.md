# Care360 Android Builder — separate project infrastructure

This repository is public and belongs to the SpeakOut GitHub organization for technical administration. **Care360 is a separate healthcare project**: its confidential source, costs, data, applications and business operations remain under Care360Apps.

## Verified

- [Public Ubuntu runner smoke test passed (Nov 6, 2026)](https://github.com/speakoutMentalHealth/care360-android-builder/actions/runs/42251837304).
- [Public authenticated artifact encryption tests passed](https://github.com/speakoutMentalHealth/care360-android-builder/actions/runs/42254448287).
- **A Care360 APK has NOT yet been built in this repository.** The build workflow is manual-only and requires two encrypted repository secrets before it can start.

## Secure Care360 synthetic build workflow

Workflow: [`.github/workflows/care360-patient-offline-encrypted.yml`](.github/workflows/care360-patient-offline-encrypted.yml)

The workflow:
1. Runs only when manually dispatched by a collaborator with repository write access.
2. Checks for a properly scoped private-source token and a long output-encryption password **before** checkout and compilation.
3. Checks out exactly the reviewed 40-character commit from the separate private `Care360Apps/k3-patient` repository. Never copies its code into this public Git repository.
4. Generates only synthetic offline Firebase and a `.invalid` API endpoint, runs focused tests, and attempts an ARM64 debug build.
5. Redirects dependency/Flutter/Gradle output to a private runner log. It does not print source excerpts or error stack traces to the publicly visible job log.
6. Uses AES-256-GCM authenticated encryption with a PBKDF2-derived key to package any resulting APK and diagnostics.
7. Uploads **only encrypted ciphertext** as a one-day public artifact. The runner's unencrypted files are temporary and never uploaded.

**Limitations:** A publicly hosted workflow still runs proprietary code on a GitHub-managed ephemeral machine. Its metadata and ordinary workflow logs are public. Never put real API keys, live Firebase config, clinical data, patient identifiers, production signing keys, or real credentials into this synthetic workflow. A compiled APK is *not* proof of a functioning app. GitHub may impose usage policies or additional restrictions. For production/staging build and protected artifact delivery, prefer a private CI environment and dedicated Care360 billing.

## Administrator setup — required once

**Do not paste secrets into a PR, issue, chat message, log, or repository file.**

1. While signed into an account authorized for `Care360Apps/k3-patient`, open your GitHub profile **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   - Resource owner: `Care360Apps` (subject to its token approval policy).
   - Repository access: **Only select repositories → k3-patient**.
   - Repository permissions: **Contents: Read-only** (Metadata: Read-only automatically).
   - Expiration: as short as practical (e.g. 7 days). No Actions/write/admin permissions.
2. Open this repository's [Actions secrets settings](https://github.com/speakoutMentalHealth/care360-android-builder/settings/secrets/actions), select **New repository secret**, and create **`CARE360_SOURCE_READ_TOKEN`** containing that fine-grained token.
3. Generate a *separate* unpredictable, preferably password-manager-generated 40–64+ character secret. Store it privately; you will need it to decrypt downloaded output. Create the repository secret **`K3_BUILD_OUTPUT_PASSWORD`** with that value. Do not reuse passwords, API keys or the source token.
4. Restrict write access to this public repository to trusted maintainers. Do not create a `pull_request_target` trigger or run checkout+secrets on untrusted pull requests.

After secrets are configured, navigate to [Actions](https://github.com/speakoutMentalHealth/care360-android-builder/actions) → **Care360 Patient synthetic debug - encrypted output** → **Run workflow**.

Default pinned source SHA is `615ceb049609796be76bd3ffee33b8e050b434ca` (recorded Nov 6, 2026). **Verify it still corresponds to the desired reviewed [PR #27](https://github.com/Care360Apps/k3-patient/pull/27) commit before running.** The workflow will refuse non-40-character inputs.

If compilation succeeds, the one-day run artifact includes `Care360-Patient-OFFLINE-debug.tar.gz.k3enc`, **not a public APK**. If compilation fails, the encrypted bundle will contain diagnostic logs only. No uploaded plain-text build logs or plain APKs are permitted.

## How to open an encrypted artifact (no laptop compilation required)

From any computer with Python 3 installed, get `scripts/k3_artifact_crypto.py` from this public repository, then:

```shell
python -m pip install cryptography
python scripts/k3_artifact_crypto.py --decrypt --prompt-password Care360-Patient-OFFLINE-debug.tar.gz.k3enc Care360-Patient-OFFLINE-debug.tar.gz
tar -xzf Care360-Patient-OFFLINE-debug.tar.gz
```

Enter the long password from your password manager when prompted. This is **decryption only**, not building. The archive contains `BUILD-INFO.txt`, optional `build-log.txt`, and the APK if compilation succeeded. The APK is a **disconnected offline design/smoke-test build**: it cannot sign into Care360 or use live services. Do not distribute it as a production release.

## What must still be verified

- A successful cloud Flutter dependency setup, focused tests and Android build.
- Actual startup beyond the logo on supported devices and Android versions.
- Production-grade secure storage / Fluttertoast Android compatibility.
- Correct staging authentication, appointments and role-gated features.
- Separate private build and delivery flow for any clinical/staging/release APK.

Build resource costs and any paid services must be attributed to Care360, not SpeakOut Mental Health programme expenses.
