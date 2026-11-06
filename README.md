# Care360 Android Builder — public infrastructure checks

This **public** repository belongs to the SpeakOut GitHub organization but is reserved for technical build-infrastructure experiments for the **separate Care360 project**. It is not part of SpeakOut's mental-health application, organizational finances, or programme deliverables.

## Verified runner availability
The minimal [public runner smoke workflow](.github/workflows/public-runner-smoke.yml) completed successfully on November 6, 2026: [run #42251837304](https://github.com/speakoutMentalHealth/care360-android-builder/actions/runs/42251837304).

- Uses pinned `ubuntu-24.04`, not the moving `ubuntu-latest` label.
- Checks OS architecture, memory, free disk and Java.
- Does **not** fetch private Care360 code, read secrets, build APKs or upload artifacts.
- No production API, Firebase, patient data or clinical services are involved.

## Security and compliance before private-source builds

Care360 Patient is a **private** repository at `Care360Apps/k3-patient`; its startup fixes are under review in [PR #27](https://github.com/Care360Apps/k3-patient/pull/27). Public GitHub workflow logs, steps and uploaded artifacts can be viewed by others. This public builder therefore **must not** be configured to clone that private repository or emit proprietary source/build artifacts until the organization approves a secure, billing-compliant workflow with private artifact delivery and tightly scoped credentials.

If a future workflow uses an access token:
- Use a short-lived GitHub App installation token or minimally scoped fine-grained PAT, saved only as an encrypted Actions secret; never commit it.
- Lock execution to trusted maintainers with manual dispatch; no untrusted pull-request execution, workflow-script injection, or fork-triggered secrets.
- Verify source and output access licensing, artifact retention, privacy controls and allowed GitHub Actions usage before committing a build workflow.
- Never upload unencrypted clinical-configured APKs, symbols, private source archives, secrets or patient data to public Actions artifacts or logs.
- Keep synthetic/offline, staging and production configurations independent. No production publish/merge from this repository.

## Next engineering tasks

1. Review Care360 PR #27 on the private source repository, confirm current CI/build state.
2. Choose and configure a **private artifact destination** and legitimate private-source CI access.
3. Verify build infrastructure supports the Agora/Gradle memory requirement without repeatedly retrying an OOM build.
4. Run cloud Flutter tests, Android build and Android emulator/device startup smoke tests.
5. Document APK delivery and verifiable pass/fail evidence. No production release until staging acceptance passes.
