#!/usr/bin/env python3
"""CineFlow UI customisation applied to the upstream CloudStream checkout.

Modifications (all deterministic, applied to upstream `master`):
  1. Bottom navigation shows only Home and Library.
  2. A settings button is added to the Home top bar, next to the account button.
  3. That button is wired to the existing `navigation_settings` destination.
  4. The bottom-nav check state updates are made null-safe, because the downloads and
     settings items no longer exist in the menu.

Run from the repository root of a CloudStream checkout.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(".")

STRINGS = ROOT / "app/src/main/res/values/strings.xml"
HEAD = ROOT / "app/src/main/res/layout/fragment_home_head.xml"
HOME_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/home/HomeFragment.kt"
MAIN_ACTIVITY = ROOT / "app/src/main/java/com/lagradost/cloudstream3/MainActivity.kt"

# ---------------------------------------------------------------- 0. app name
strings = STRINGS.read_text(encoding="utf-8")
new_strings, replaced = re.subn(
    r'<string name="app_name">[^<]*</string>',
    '<string name="app_name">Prime Box</string>',
    strings,
)
if replaced != 1:
    sys.exit("[ui] app_name string not found in values/strings.xml")
STRINGS.write_text(new_strings, encoding="utf-8")
print("[ui] app name -> Prime Box")

# ---------------------------------------------------------------- 1. bottom nav
# Left exactly as upstream: the navigation menu is no longer overridden.
print("[ui] bottom_nav_menu.xml -> untouched (upstream layout kept)")

# ------------------------------------------- 2. settings button in the home top bar
head = HEAD.read_text(encoding="utf-8")
if "home_head_settings" not in head:
    anchor = (
        '            <LinearLayout\n'
        '                android:id="@+id/home_head_profile_padding"'
    )
    if anchor not in head:
        sys.exit("[ui] anchor for the profile button not found in fragment_home_head.xml")
    block = (
        '            <LinearLayout\n'
        '                android:id="@+id/home_head_settings"\n'
        '                android:layout_width="44dp"\n'
        '                android:layout_height="44dp"\n'
        '                android:clickable="true"\n'
        '                android:focusable="true"\n'
        '                android:foreground="@drawable/rounded_select_ripple"\n'
        '                android:gravity="center"\n'
        '                android:orientation="horizontal">\n'
        '\n'
        '                <ImageView\n'
        '                    android:layout_width="23dp"\n'
        '                    android:layout_height="23dp"\n'
        '                    android:contentDescription="@string/title_settings"\n'
        '                    android:src="@drawable/settings_icon_selector" />\n'
        '            </LinearLayout>\n'
        '\n'
    )
    head = head.replace(anchor, block + anchor, 1)
    HEAD.write_text(head, encoding="utf-8")
    print("[ui] fragment_home_head.xml -> settings button added next to the account button")

# ------------------------------------------- 3. wire the settings button
frag = HOME_FRAGMENT.read_text(encoding="utf-8")
if "home_head_settings" not in frag:
    marker = (
        "            homeSwitchAccount.setOnClickListener {\n"
        "                activity?.showAccountSelectLinear()\n"
        "            }\n"
    )
    if marker not in frag:
        sys.exit("[ui] account click handler not found in HomeFragment.kt")
    addition = marker + (
        "\n"
        "            binding.root.findViewById<View>(R.id.home_head_settings)?.setOnClickListener {\n"
        "                runCatching {\n"
        "                    androidx.navigation.fragment.NavHostFragment.findNavController(this@HomeFragment)\n"
        "                        .navigate(R.id.navigation_settings)\n"
        "                }\n"
        "            }\n"
    )
    frag = frag.replace(marker, addition, 1)
    HOME_FRAGMENT.write_text(frag, encoding="utf-8")
    print("[ui] HomeFragment.kt -> settings button wired to navigation_settings")

# ------------------------------------------- 4. null-safe bottom-nav check updates
activity = MAIN_ACTIVITY.read_text(encoding="utf-8")
pairs = [
    (
        "                    navRailView.menu.findItem(R.id.navigation_downloads).isChecked = true\n"
        "                    navView.menu.findItem(R.id.navigation_downloads).isChecked = true\n",
        "                    navRailView.menu.findItem(R.id.navigation_downloads)?.isChecked = true\n"
        "                    navView.menu.findItem(R.id.navigation_downloads)?.isChecked = true\n",
    ),
    (
        "                    navRailView.menu.findItem(R.id.navigation_settings).isChecked = true\n"
        "                    navView.menu.findItem(R.id.navigation_settings).isChecked = true\n",
        "                    navRailView.menu.findItem(R.id.navigation_settings)?.isChecked = true\n"
        "                    navView.menu.findItem(R.id.navigation_settings)?.isChecked = true\n",
    ),
]
changed = 0
for old, new in pairs:
    if old in activity:
        activity = activity.replace(old, new, 1)
        changed += 1
if changed != 2:
    sys.exit(f"[ui] expected 2 bottom-nav check updates, patched {changed}")
MAIN_ACTIVITY.write_text(activity, encoding="utf-8")
print("[ui] MainActivity.kt -> bottom-nav check updates are null-safe")

print("[ui] customisation complete")
