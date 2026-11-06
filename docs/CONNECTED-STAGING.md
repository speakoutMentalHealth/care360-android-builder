# Connected Care360 Patient staging APK — private source, public runner

This is a separate, **manual-only** route for getting a real **staging-connected** APK when the private Care360Apps runner is unavailable. It does not change the existing working **offline synthetic** build. The two APKs are intentionally distinct.

## Configure before running

In [SpeakOut Care360 Android Builder repository secrets](https://github.com/speakoutMentalHealth/care360-android-builder/settings/secrets/actions), keep the existing:
- `CARE360_SOURCE_READ_TOKEN`: fine-grained token with read-only Contents permission on **Care360Apps/k3-patient only**.
- `K3_BUILD_OUTPUT_PASSWORD`: separately generated random password of 32+ characters. Store privately; do not paste into chats.

Add two **secrets** to this public builder:
- `K3_STAGING_API_URL`: the explicitly approved *nonproduction* HTTPS API, with a staging/sandbox/test/dev hostname and path ending exactly `/api/`. An admin UI URL is not automatically an API URL.
- `K3_STAGING_ANDROID_FIREBASE_JSON_B64`: base64-encoded Android `google-services.json` from the isolated staging Firebase project, registering package **`com.cnu.patient.k3staging`**, not `com.cnu.patient`. Do not upload the JSON or base64 text to the repository, issue, or chat. Use the existing staging Firebase project only after checking separation.

Add two **repository variables**:
- `K3_STAGING_FIREBASE_PROJECT_ID`: exact staging Firebase Project ID matching the Android JSON.
- `K3_STAGING_API_VERIFIED`: set to `true` **only after** a developer independently confirms API, payment, notification, Firebase, and data isolation. Leave unset or false otherwise. Do not use a production API or production database.

The workflow fails closed if these safeguards are missing. It also rejects an HTTP/IP/localhost/production-looking API and refuses Firebase configs that contain the real Patient package.

## Run

1. Open [Actions in the builder](https://github.com/speakoutMentalHealth/care360-android-builder/actions) and select **Care360 Patient CONNECTED staging debug - encrypted output**.
2. Choose **Run workflow** and pin the exact Patient source commit. The default revision is the same private source SHA already compiled by the synthetic builder; replace it if an approved, tested revision is newer.
3. If the run succeeds, download **Care360-Patient-STAGING-debug-ENCRYPTED**. If compilation fails, the encrypted archive contains `build-log.txt`; it will not expose private source diagnostics in public logs.
4. Decrypt locally with the existing [Windows decryptor workflow](https://github.com/speakoutMentalHealth/care360-android-builder/actions/workflows/windows-decryptor.yml) and your saved output password, then extract `Care360-Patient-STAGING-debug.apk`.
5. Install APK on an **ARM64** BlueStacks instance; this staging app uses a separate package ID so it cannot replace the production Patient app. Create and sign into a disposable *staging* Patient account; no real patients, payments, or clinical use.

## Troubleshooting

- **Login disabled and OFFLINE DESIGN TEST banner:** You installed the synthetic APK. Install the `STAGING` APK instead.
- **Staging build prerequisite error:** Check secrets, variables, staging URL and Android Firebase package registration. Do not relax checks to make a production URL pass.
- **Build fails:** Decrypt `build-log.txt` locally. Share only the smallest **redacted** error excerpt, without patient data, tokens or server responses.
- **Build succeeds but staging login fails:** Confirm backend reachability and correct Firebase custom-token project, verify a test account exists, and inspect connection diagnostics. Successful compilation does not prove sign-in works.
- **FlutterError / screen could not be displayed:** Capture a short BlueStacks `adb logcat` trace around the failing navigation. The privacy-preserving on-screen message alone does not identify the failed widget.

The build does not change or deploy Care360 Patient source code. Source changes belong in reviewed Patient repository PRs. This runner only builds an exact, pinned private revision, packages artifacts under AES-GCM authenticated encryption, and retains ciphertext for one day.
