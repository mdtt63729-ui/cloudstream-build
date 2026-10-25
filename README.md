# CloudStream build (GPL-3.0)

This repository builds the **CloudStream** Android app and signs the release APK.

## Licence: GNU General Public License v3.0

The application produced by this repository is **CloudStream**, which is licensed under the
**GNU General Public License, version 3** — see [LICENSE](LICENSE).

GPL-3.0 requires that everyone who receives a binary can also obtain the corresponding source
code. The complete source is:

- Upstream: <https://github.com/recloudstream/cloudstream> (branch `master`)
- The exact commit used for a build is the `Checkout CloudStream` step of that workflow run; it
  checks out upstream `master` and the commit SHA is printed in the run log.

This repository contains **no application source of its own**. It only holds the CI workflow
`.github/workflows/build-cloudstream.yml`, which checks out upstream at build time, builds, and
signs. That workflow file is released under GPL-3.0 as well, for consistency with the app it
produces.

## Build

- JDK 21
- Android SDK platform 37, build-tools 37.0.0
- Gradle 9.4.1 (from the upstream wrapper)
- Task: `./gradlew :app:assembleStableRelease`

Gradle produces an **unsigned** release APK; the workflow then signs it with `apksigner` using the
keystore held in this repository's Actions secrets:

| Secret | Meaning |
| --- | --- |
| `SIGNING_KEYSTORE_BASE64` | the release keystore, base64 encoded |
| `SIGNING_STORE_PASSWORD` | keystore password |
| `SIGNING_KEY_ALIAS` | key alias |
| `SIGNING_KEY_PASSWORD` | key password |

If those secrets are absent the workflow generates a throwaway keystore, signs, and uploads it —
so the same key is not reused between builds in that case. With the secrets present, every build
is signed with the same key and installs as an update over the previous one.

## Redistribution

If you redistribute the APK, keep this licence with it and offer the source above. CloudStream is
third-party software. The extensions a user installs are separate third-party works and carry
their own terms; this repository does not bundle or distribute any extension.

## Local modifications (GPL-3.0 corresponding source)

The build applies these local modifications to upstream `master`. They are reproduced
deterministically by [`assets/patch_ui.py`](assets/patch_ui.py) together with the artwork in
[`assets/icons/`](assets/icons), which are part of this repository:

1. **Launcher icon** replaced with the artwork in `assets/icons/` — adaptive foreground/background,
   legacy and round mipmaps, and the 512 px Play Store icon.
2. **Bottom navigation** reduced to **Home** and **Library** only.
3. **Settings button** added to the Home top bar, immediately left of the account button, wired to
   the existing `navigation_settings` destination.
4. The bottom-navigation check-state updates in `MainActivity.kt` are made null-safe, because the
   downloads and settings entries no longer exist in the menu.

Upstream `master` plus the files in this repository are therefore the complete corresponding
source for the APKs published here.
