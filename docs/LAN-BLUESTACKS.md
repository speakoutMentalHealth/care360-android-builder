# Care360 Patient LAN-connected debug on BlueStacks

**Purpose:** Use a local Laravel test backend on the laptop, plus isolated Firebase staging, to test *real* Patient sign-in while keeping the production Patient app and patient data untouched. This is an **Android DEBUG-only** workflow; not for real patient data, clinical care, payments, or production accounts.

The workflow uses the secure private-source + encrypted-output pattern from the working offline builder, but it **does not use the fake offline API**. It compiles private Patient source pinned to a reviewed SHA on the public runner; the laptop backend is contacted later by BlueStacks, not by the GitHub runner.

## Requirements

In [Care360 Android Builder repository Settings → Secrets and variables → Actions](https://github.com/speakoutMentalHealth/care360-android-builder/settings/secrets/actions):

- Keep existing **secret** `CARE360_SOURCE_READ_TOKEN` (read-only access to `Care360Apps/k3-patient`) and **secret** `K3_BUILD_OUTPUT_PASSWORD` (32+ random characters). Do not paste either into chat or issues.
- Add **secret** `K3_STAGING_ANDROID_FIREBASE_JSON_B64`. This is the base64 of *staging* Android `google-services.json`, with exactly one matching `com.cnu.patient.k3staging` registration. It may be available in the private Patient repository's existing Actions secrets; GitHub cannot display an existing secret value. Obtain the original staging JSON from the Firebase console instead. Keep production `cnu-medical` out.
- Add **variable** `K3_STAGING_FIREBASE_PROJECT_ID` with the approved staging Firebase Project ID (`care360-staging-9c90a` from the prior staging setup; verify against the Firebase console before use).
- After confirming the **local Laravel database contains only fictional test data and no genuine patient information**, add **variable** `K3_LAN_LOCAL_DATA_VERIFIED` = `true`. Do not set it merely to pass the build.
- Make sure your laptop's firewall allows BlueStacks to reach Laravel on port 8000, then run Laravel on a trusted local network interface. Avoid exposing port 8000 to the public internet.

## Run

1. Open [Care360 Patient LAN-connected debug — encrypted output](https://github.com/speakoutMentalHealth/care360-android-builder/actions/workflows/care360-patient-lan-encrypted.yml).
2. Click **Run workflow**. Source SHA defaults to the isolated Patient PR preview build. Check the current laptop IPv4 with `ipconfig` in Windows and update the workflow's `backend_ipv4` input if needed. `192.168.0.101` is only the *last recorded* laptop address, not confirmed current.
3. A successful job uploads **Care360-Patient-LAN-debug-ENCRYPTED**. Download it and use the existing [Windows decryptor](https://github.com/speakoutMentalHealth/care360-android-builder/actions/workflows/windows-decryptor.yml) with your saved password. The tarball contains `Care360-Patient-LAN-debug.apk`, `build-log.txt` and `BUILD-INFO.txt`.
4. Install on an **ARM64** BlueStacks instance while the local Laravel test API is running. If Android rejects installation with an update signature mismatch, uninstall only the previous test package `com.cnu.patient.k3staging`; do not uninstall the production Care360 Patient app.
5. Sign in with a fictional staging Patient account from the local Laravel database. Test doctor discovery, pharmacy listings and navigation. A successful APK build does **not** guarantee Laravel, Firebase custom tokens, Firestore rules or appointments work.

## Safeguards

The source helper `tools/k3_lan_build_config.py` rejects public IPv4 addresses, requires the dedicated Firebase staging project and isolated package, and allows cleartext HTTP **only in the Android debug manifest**. The workflow explicitly requires test-data approval and never prints raw source build logs or Firebase config publicly. Artifacts are encrypted, retained for one day, and not suitable for clinic deployment.

**Do not** insert a production API URL, use production Firebase app keys, or set authentication state manually to bypass sign-in. The `K3_OFFLINE_TEST` walkthrough remains separate and is not enabled in this connected LAN build.
