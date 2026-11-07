# Care360 Patient Maps — staging-only LAN debug review

Purpose: Fix the BlueStacks address screen showing "Google Maps API key is missing" without committing an unrestricted API key or modifying any production Android signing configuration.

The CI-only [Maps/signing helper](../scripts/k3_prepare_patient_maps_signing.py) patches the **ephemeral** private Patient source checkout after the LAN staging script has added `com.cnu.patient.k3staging`. It is never used for release builds. It checks that the persistent staging certificate SHA-1 matches the approved value, refuses unexpected manifest/Gradle layouts, sets a debug-only signer, and places the restricted Maps key into the merged manifest. The key is necessarily embedded in an Android app; security depends on enforcing **both Android package+SHA-1 restrictions and Maps SDK for Android API restrictions** in Google Cloud. Never use a live billing key or a production signing certificate.

## Owner preparation (on Windows; do not paste secrets in chat)

1. In Google Cloud select the approved staging project. Enable **Maps SDK for Android**. Create a dedicated API key, restrict it to **Maps SDK for Android**, and restrict application access to **Android apps** with package `com.cnu.patient.k3staging` and the SHA-1 of the **staging certificate** below. Complete restriction and save before using the key. Maps billing restrictions and alerts remain the owner's responsibility.

2. Use the persistent **test-only** PKCS12 signing file `C:\care360\private-keys\care360-patient-staging.jks`. If it was created using the previous PowerShell steps, do **not** regenerate it: signing identities must remain stable. If it does not exist, create a dedicated nonproduction PKCS12 certificate using `keytool -genkeypair -storetype PKCS12 ... -alias care360-patient-staging`. Save its password in a password manager, not a repository file.

3. From PowerShell, using the correct keytool on PATH, inspect the SHA-1 **without sending the keystore or password**:

```powershell
keytool -list -v -storetype PKCS12 -keystore "C:\care360\private-keys\care360-patient-staging.jks" -alias care360-patient-staging | Select-String 'SHA1:'
```

4. Store these in **speakoutMentalHealth/care360-android-builder → Settings → Secrets and variables → Actions**:

| Type | Name | Content |
| --- | --- | --- |
| Repository secret | `K3_STAGING_MAPS_ANDROID_API_KEY` | Maps SDK key restricted in Google Cloud; never share it here |
| Repository secret | `K3_STAGING_PATIENT_DEBUG_KEYSTORE_B64` | Base64-encoded contents of the **test-only** PKCS12 keystore |
| Repository secret | `K3_STAGING_PATIENT_KEYSTORE_PASSWORD` | Its private signing password, 16+ characters |
| Repository variable | `K3_STAGING_PATIENT_SIGNING_SHA1` | The 20-byte colon-separated uppercase staging SHA-1 (public fingerprint, not a private key) |

To copy keystore bytes to clipboard without printing them:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\care360\private-keys\care360-patient-staging.jks")) | Set-Clipboard
```

Keep the previous isolated test-only database, Firebase and source-token checks enabled. Do **not** share password, keystore, Base64, or Maps key in chat.

5. Manually run `Care360 Patient LAN-connected debug - encrypted output` on **branch** `fix/patient-lan-maps-staging-signed-20261107`, with the reviewed private Patient SHA `a2874477cf04dc0bc28d7a8d5fb597eef3453ac0` and your actual private LAN IPv4 address. Running on `main` would use the previous build workflow and leave Maps missing.

6. Download the **encrypted** artifact, decrypt privately using the existing encrypted-artifact mechanism, and install the debug APK. A new signing certificate means Android may refuse update over the previous `.k3staging` build: uninstall **only** `com.cnu.patient.k3staging`, not the production Patient app. Sign in with fictional test users and verify address-map tiles; report screenshot and any Maps authorization errors. Do not enter real patient data or make live bookings/payments.

## Validation status

The helper was locally exercised with a synthetic PKCS12 keystore and placeholder manifest/Gradle fixture. End-to-end GitHub build and BlueStacks Map tiles **have not yet been tested** on the owner setup. This is a **draft review change**, not production-approval or publisher handover.
