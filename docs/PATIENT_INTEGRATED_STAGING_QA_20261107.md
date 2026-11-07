# Care360 Patient — integrated Nigerian-first UI / sponsors / language / AI QA APK

**For owner review on BlueStacks only. Not a Play Store or production build.**

This staged follow-up branch builds from the Maps/stable-test-signature builder draft and pins the **private Patient PR #35** integrated source.

- Public builder branch: `feat/patient-integrated-stage-qa-20261107`
- Pinned reviewed Patient source commit: `c0edb9f1e4bd48f0fed09bdb5998b4b2d7e3417b`
- Private source review: `Care360Apps/k3-patient` PR #35; upstream Nearby Care PR #33 is unmerged.
- Uses **the same** existing, restricted Maps Android key, staged PKCS12 keystore, test-only Firebase and output-encryption secrets. No new passwords or private keys required.
- The `backend_ipv4` workflow input has **no default**; enter your laptop's current RFC1918 IPv4 on the trusted test LAN. Start isolated Laravel port 8000 before login. Use **fictional** Patient/Doctor/Provider accounts only.
- Workflow runs existing startup and offline tests, **plus** sponsor ten-second rotation/HTTPS, dedicated AI Guide shortcut, responsive African-clinician hero and five-language UI/fallback tests before assembling the encrypted APK.

## What to review in the updated test APK

1. Confirm all CI tests pass and encrypted bundle includes the APK. Failure means inspect only the encrypted diagnostic log using your existing local decryptor. **Do not upload plaintext APK or logs to public GitHub.**
2. Install only the app labeled **Care360 Patient LAN TEST**, package `com.cnu.patient.k3staging`. This should preserve the staging signing identity from the earlier Maps build. If Android reports a signer mismatch, uninstall **only this staging app**; never production Care360.
3. Authenticate with existing local synthetic Patient account. Verify existing dashboard, map tiles/address, opt-in Nearby Care, appointment and provider navigation.
4. Confirm the dark navy/teal `Care closer to home` hero shows the existing African-clinician asset (or graceful icon fallback); **Find nearby care** opens the existing Map View.
5. Open **Care360 Guide**, choose help topic, verify the curated answer. Remote generative AI must be **OFF** in this LAN HTTP build and no patient prompts/medical records should be sent to any model.
6. On Patient Home, verify exactly **one** separate partner/sponsor carousel. MindCheck identified as an external SpeakOut partner. Approved banners have `Sponsored` labels; slide advances at 10 seconds, manual arrows/dots work and external HTTPS destination opens only with user action. No sponsor ads on prescriptions/consultations.
7. Switch English / Hausa / Igbo / Yoruba / French; verify picker appears and preference persists after relaunch. **Language coverage is intentionally incomplete**: Patient JSON ≈ 11% per non-English locale and Plus JSON ≈ 11%; missing keys fall back to English. Native review is a separate release blocker.
8. Report screenshots and functional issues only, with fictional data and no secrets, tokens or medical files.


9. In **Add Address**, if the legacy Places search key is absent, tap an exact point **on the displayed map**, enter the location label and human-readable street address, and press **Add Address**. Verify the address saves and displays in the fictional Patient account. Search by name remains unavailable until Places is migrated to a separately secured native SDK or authenticated Laravel proxy; never put a server-side Places web-service key in the APK or public settings response.


10. **Language crash regression:** from a signed-in Patient page tap the persistent language icon, select Hausa, wait for the modal to close and verify the screen remains alive. Repeat with Igbo, Yoruba, French and English, also using Settings > Change Language. Close/reopen the app to check persistence. The source fix waits for the popup or Settings route to complete before rebuilding MaterialApp; this is a candidate fix and is **not proven on BlueStacks** until tested.
11. **Updated visual identity:** confirm the formerly electric-blue Home, cards, action buttons and tabs use the navy/medical-teal palette consistently, without invisible text or overflow at 320px and system font scaling. Capture screenshots of sign-in, Home, Nearby Care, booking, prescriptions, Profile and language picker; review the original African-clinician artwork rights and relevance before publisher sign-off.

## Release gates
CI status alone is not proof that maps, backend ad management, clinical workflows or AI generation function. Backend sponsor admin PR #18 is unmerged; AI backend pilot PR #8 remains disabled. Clinical/privacy and infrastructure blockers remain open. Developer handles production signing and all Play Store uploads. Keep product and SpeakOut finances separately tracked.
