#!/usr/bin/env python3
"""Prime Box UI customisation applied to the upstream CloudStream checkout.

Applied deterministically to upstream `master`:
  0. App name -> Prime Box.
  1. Bottom navigation -> Home + Library only.
  2. Library tab opens a new card home (Download / Recent / History / Offline).
  3. Settings button in the Home top bar next to the account button.
  4. Bottom-nav check updates made null-safe.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(".")
STRINGS = ROOT / "app/src/main/res/values/strings.xml"
MENU = ROOT / "app/src/main/res/menu/bottom_nav_menu.xml"
NAVGRAPH = ROOT / "app/src/main/res/navigation/mobile_navigation.xml"
HEAD = ROOT / "app/src/main/res/layout/fragment_home_head.xml"
HOME_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/home/HomeFragment.kt"
MAIN_ACTIVITY = ROOT / "app/src/main/java/com/lagradost/cloudstream3/MainActivity.kt"

LIB_LAYOUT = ROOT / "app/src/main/res/layout/fragment_library_home.xml"
LIB_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/library/LibraryHomeFragment.kt"
CARD_BG = ROOT / "app/src/main/res/drawable/pb_card_bg.xml"
TILE_BG = ROOT / "app/src/main/res/drawable/pb_card_tile_bg.xml"

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
MENU.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<menu xmlns:android="http://schemas.android.com/apk/res/android">
        <item
            android:id="@+id/navigation_home"
            android:icon="@drawable/home_icon_selector"
            android:title="@string/title_home" />
        <item
            android:id="@+id/navigation_library"
            android:icon="@drawable/library_icon_selector"
            android:title="@string/library" />
</menu>
""",
    encoding="utf-8",
)
print("[ui] bottom_nav_menu.xml -> Home + Library")

# ---------------------------------------------------------------- 2. library card home
CARD_BG.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#221C1A" />
    <corners android:radius="26dp" />
</shape>
""",
    encoding="utf-8",
)
TILE_BG.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#3A2E29" />
    <corners android:radius="18dp" />
</shape>
""",
    encoding="utf-8",
)


def card(card_id: str, label: str, icon: str) -> str:
    return f"""
        <LinearLayout
            android:id="@+id/{card_id}"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginBottom="14dp"
            android:background="@drawable/pb_card_bg"
            android:clickable="true"
            android:focusable="true"
            android:foreground="?attr/selectableItemBackground"
            android:gravity="center_vertical"
            android:orientation="horizontal"
            android:padding="16dp">

            <ImageView
                android:layout_width="56dp"
                android:layout_height="56dp"
                android:background="@drawable/pb_card_tile_bg"
                android:contentDescription="@null"
                android:padding="14dp"
                android:src="@drawable/{icon}"
                app:tint="#F0A58F" />

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_marginStart="16dp"
                android:text="{label}"
                android:textColor="#F5EAE6"
                android:textSize="20sp"
                android:textStyle="bold" />
        </LinearLayout>
"""


LIB_LAYOUT.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#141010"
    android:fillViewport="true">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="18dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:paddingBottom="16dp"
            android:text="@string/library"
            android:textColor="#F5EAE6"
            android:textSize="26sp"
            android:textStyle="bold" />
"""
    + card("card_download", "Download", "netflix_download")
    + card("card_recent", "Recent", "home_icon_selector")
    + card("card_history", "History", "library_icon_selector")
    + card("card_offline", "Offline", "netflix_download")
    + """
    </LinearLayout>
</ScrollView>
""",
    encoding="utf-8",
)
print("[ui] fragment_library_home.xml -> 4 cards")

LIB_FRAGMENT.write_text(
    """package com.lagradost.cloudstream3.ui.library

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.NavHostFragment
import com.lagradost.cloudstream3.R

/**
 * Prime Box library home: Download / Recent / History / Offline cards.
 * Download opens the existing downloads screen; the other three are wired in the next steps.
 */
class LibraryHomeFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_library_home, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val nav = NavHostFragment.findNavController(this)

        view.findViewById<View>(R.id.card_download)?.setOnClickListener {
            runCatching { nav.navigate(R.id.navigation_downloads) }
                .onFailure { toast("Downloads could not be opened") }
        }
        view.findViewById<View>(R.id.card_recent)?.setOnClickListener { toast("Recent: next step") }
        view.findViewById<View>(R.id.card_history)?.setOnClickListener { toast("History: next step") }
        view.findViewById<View>(R.id.card_offline)?.setOnClickListener { toast("Offline: next step") }
    }

    private fun toast(message: String) {
        runCatching { Toast.makeText(requireContext(), message, Toast.LENGTH_SHORT).show() }
    }
}
""",
    encoding="utf-8",
)
print("[ui] LibraryHomeFragment.kt written")

# point the library destination at the new card home
graph = NAVGRAPH.read_text(encoding="utf-8")
old_name = "com.lagradost.cloudstream3.ui.library.LibraryFragment"
new_name = "com.lagradost.cloudstream3.ui.library.LibraryHomeFragment"
if new_name not in graph:
    if old_name not in graph:
        sys.exit("[ui] LibraryFragment destination not found in mobile_navigation.xml")
    graph = graph.replace(old_name, new_name, 1)
    NAVGRAPH.write_text(graph, encoding="utf-8")
    print("[ui] mobile_navigation.xml -> navigation_library opens the card home")

# ---------------------------------------------------------------- 3. settings button
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
    print("[ui] fragment_home_head.xml -> settings button added")

# ---------------------------------------------------------------- 4. wire settings button
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
    print("[ui] HomeFragment.kt -> settings button wired")

# ---------------------------------------------------------------- 5. null-safe nav checks
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
