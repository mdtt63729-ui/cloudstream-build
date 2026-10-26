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
if 'name="pb_me"' not in new_strings:
    new_strings = new_strings.replace(
        "</resources>",
        '    <string name="pb_me">Me</string>\n</resources>',
        1,
    )
STRINGS.write_text(new_strings, encoding="utf-8")
print("[ui] app name -> Prime Box, added string pb_me")

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
        <item
            android:id="@+id/navigation_settings"
            android:icon="@drawable/settings_icon_selector"
            android:title="@string/pb_me" />
</menu>
""",
    encoding="utf-8",
)
print("[ui] bottom_nav_menu.xml -> Home + Library + Me")

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

# ---------------------------------------------------------------- 3. top bar: logo + search
LOGO = ROOT / "app/src/main/res/drawable/pb_logo.png"
SEARCH_BG = ROOT / "app/src/main/res/drawable/pb_search_bg.xml"
src_logo = pathlib.Path("overlay/assets/icons/ic_launcher-xxxhdpi.png")
if src_logo.exists():
    LOGO.write_bytes(src_logo.read_bytes())
    print("[ui] pb_logo.png written from the launcher artwork")

SEARCH_BG.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="#2A2624" />
    <corners android:radius="24dp" />
</shape>
""",
    encoding="utf-8",
)

head = HEAD.read_text(encoding="utf-8")

# 3a. app logo to the left of the search bar
if "pb_logo" not in head:
    search_anchor = (
        '            <androidx.appcompat.widget.SearchView\n'
        '                android:id="@+id/home_search"'
    )
    if search_anchor not in head:
        sys.exit("[ui] home_search SearchView not found in fragment_home_head.xml")
    logo_block = (
        '            <ImageView\n'
        '                android:id="@+id/pb_logo"\n'
        '                android:layout_width="34dp"\n'
        '                android:layout_height="34dp"\n'
        '                android:layout_marginEnd="8dp"\n'
        '                android:contentDescription="@string/app_name"\n'
        '                android:src="@drawable/pb_logo" />\n'
        '\n'
    )
    head = head.replace(search_anchor, logo_block + search_anchor, 1)

# 3b. rounded search bar
head = head.replace(
    '                android:padding="0dp"\n                android:textColor="@color/white"',
    '                android:padding="0dp"\n'
    '                android:background="@drawable/pb_search_bg"\n'
    '                android:paddingHorizontal="10dp"\n'
    '                android:textColor="@color/white"',
    1,
)

# 3c. green "Search" label + hidden settings view, before the profile avatar
if "home_search_button" not in head:
    profile_anchor = (
        '            <LinearLayout\n'
        '                android:id="@+id/home_head_profile_padding"'
    )
    if profile_anchor not in head:
        sys.exit("[ui] profile anchor not found in fragment_home_head.xml")
    right_block = (
        '            <TextView\n'
        '                android:id="@+id/home_search_button"\n'
        '                android:layout_width="wrap_content"\n'
        '                android:layout_height="match_parent"\n'
        '                android:background="?attr/selectableItemBackground"\n'
        '                android:clickable="true"\n'
        '                android:focusable="true"\n'
        '                android:gravity="center"\n'
        '                android:paddingHorizontal="10dp"\n'
        '                android:text="Search"\n'
        '                android:textColor="#4ADE80"\n'
        '                android:textSize="15sp"\n'
        '                android:textStyle="bold" />\n'
        '\n'
        '            <LinearLayout\n'
        '                android:id="@+id/home_head_settings"\n'
        '                android:layout_width="1dp"\n'
        '                android:layout_height="1dp"\n'
        '                android:visibility="gone"\n'
        '                android:orientation="horizontal">\n'
        '\n'
        '                <ImageView\n'
        '                    android:layout_width="1dp"\n'
        '                    android:layout_height="1dp"\n'
        '                    android:contentDescription="@string/title_settings"\n'
        '                    android:src="@drawable/settings_icon_selector" />\n'
        '            </LinearLayout>\n'
        '\n'
    )
    head = head.replace(profile_anchor, right_block + profile_anchor, 1)

# 3d. hide the profile avatar - the account now lives under the Me tab
head = head.replace(
    '                android:id="@+id/home_head_profile_padding"\n'
    '                android:layout_width="50dp"',
    '                android:id="@+id/home_head_profile_padding"\n'
    '                android:visibility="gone"\n'
    '                android:layout_width="50dp"',
    1,
)

HEAD.write_text(head, encoding="utf-8")
print("[ui] fragment_home_head.xml -> logo + rounded search bar + Search label")

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
        "\n"
        "            binding.root.findViewById<View>(R.id.home_search_button)?.setOnClickListener {\n"
        "                runCatching {\n"
        "                    val searchView = binding.root.findViewById<androidx.appcompat.widget.SearchView>(R.id.home_search)\n"
        "                    val query = searchView?.query?.toString().orEmpty()\n"
        "                    if (query.isNotBlank()) searchView?.setQuery(query, true)\n"
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

# ---------------------------------------------------------------- 6. Recent / History
LIST_LAYOUT = ROOT / "app/src/main/res/layout/fragment_library_list.xml"
ROW_LAYOUT = ROOT / "app/src/main/res/layout/item_library_row.xml"
LIST_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/library/LibraryListFragment.kt"

LIST_LAYOUT.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#141010">

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/list"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:clipToPadding="false"
        android:padding="12dp" />

    <TextView
        android:id="@+id/empty"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_gravity="center"
        android:text="Nothing here yet"
        android:textColor="#93A1AE"
        android:textSize="14sp"
        android:visibility="gone" />
</FrameLayout>
""",
    encoding="utf-8",
)

ROW_LAYOUT.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:background="@drawable/pb_card_bg"
    android:clickable="true"
    android:focusable="true"
    android:foreground="?attr/selectableItemBackground"
    android:orientation="horizontal"
    android:padding="12dp"
    android:layout_marginBottom="10dp">

    <ImageView
        android:id="@+id/poster"
        android:layout_width="56dp"
        android:layout_height="82dp"
        android:background="@drawable/pb_card_tile_bg"
        android:contentDescription="@null"
        android:scaleType="centerCrop" />

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_gravity="center_vertical"
        android:layout_marginStart="14dp"
        android:layout_weight="1"
        android:orientation="vertical">

        <TextView
            android:id="@+id/title"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:ellipsize="end"
            android:maxLines="2"
            android:textColor="#F5EAE6"
            android:textSize="15sp"
            android:textStyle="bold" />

        <TextView
            android:id="@+id/subtitle"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginTop="3dp"
            android:ellipsize="end"
            android:maxLines="1"
            android:textColor="#93A1AE"
            android:textSize="12sp" />
    </LinearLayout>
</LinearLayout>
""",
    encoding="utf-8",
)

LIST_FRAGMENT.write_text(
    """package com.lagradost.cloudstream3.ui.library

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.NavHostFragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.lagradost.cloudstream3.R
import com.lagradost.cloudstream3.ui.home.HomeViewModel
import com.lagradost.cloudstream3.utils.DOWNLOAD_HEADER_CACHE
import com.lagradost.cloudstream3.utils.DataStoreHelper
import com.lagradost.cloudstream3.utils.DataStore.getKey
import com.lagradost.cloudstream3.utils.ImageLoader.loadImage
import com.lagradost.cloudstream3.utils.downloader.DownloadObjects
import kotlinx.coroutines.launch

/**
 * Prime Box list screen. mode=recent shows continue-watching entries (most recent first),
 * mode=history shows every title with a stored watch state.
 */
class LibraryListFragment : Fragment() {

    private data class Row(
        val name: String,
        val url: String,
        val apiName: String,
        val poster: String?,
        val subtitle: String
    )

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_library_list, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val mode = arguments?.getString("mode") ?: "recent"
        val list = view.findViewById<RecyclerView>(R.id.list)
        val empty = view.findViewById<TextView>(R.id.empty)
        list.layoutManager = LinearLayoutManager(requireContext())
        val adapter = Adapter { row -> open(row) }
        list.adapter = adapter

        viewLifecycleOwner.lifecycleScope.launch {
            val rows = runCatching {
                if (mode == "history") loadHistory() else loadRecent()
            }.getOrDefault(emptyList())
            adapter.submit(rows)
            empty.visibility = if (rows.isEmpty()) View.VISIBLE else View.GONE
        }
    }

    private suspend fun loadRecent(): List<Row> =
        HomeViewModel.getResumeWatching().orEmpty().map { item ->
            val episode = when {
                item.season != null && item.episode != null -> "S" + item.season + "E" + item.episode
                item.episode != null -> "Episode " + item.episode
                else -> ""
            }
            Row(
                item.name,
                item.url,
                item.apiName,
                item.posterUrl,
                listOf(episode, item.apiName).filter { it.isNotBlank() }.joinToString("  •  ")
            )
        }

    private suspend fun loadHistory(): List<Row> {
        val rows = mutableListOf<Row>()
        val ids: List<Int> = DataStoreHelper.getAllWatchStateIds().orEmpty()
        for (id in ids) {
            val cached: DownloadObjects.DownloadHeaderCached? =
                requireContext().getKey<DownloadObjects.DownloadHeaderCached>(
                    DOWNLOAD_HEADER_CACHE,
                    id.toString()
                )
            if (cached != null) {
                rows.add(Row(cached.name, cached.url, cached.apiName, cached.poster, cached.apiName))
            }
        }
        return rows
    }

    private fun open(row: Row) {
        runCatching {
            NavHostFragment.findNavController(this).navigate(
                R.id.global_to_navigation_results_phone,
                Bundle().apply {
                    putString("url", row.url)
                    putString("apiName", row.apiName)
                    putString("name", row.name)
                }
            )
        }
    }

    private class Adapter(private val onClick: (Row) -> Unit) : RecyclerView.Adapter<Adapter.Holder>() {
        private val items = mutableListOf<Row>()

        fun submit(list: List<Row>) {
            items.clear()
            items.addAll(list)
            notifyDataSetChanged()
        }

        override fun getItemCount(): Int = items.size

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder =
            Holder(LayoutInflater.from(parent.context).inflate(R.layout.item_library_row, parent, false))

        override fun onBindViewHolder(holder: Holder, position: Int) {
            val row = items[position]
            holder.title.text = row.name
            holder.subtitle.text = row.subtitle
            runCatching { holder.poster.loadImage(row.poster) }
            holder.itemView.setOnClickListener { onClick(row) }
        }

        class Holder(view: View) : RecyclerView.ViewHolder(view) {
            val poster: ImageView = view.findViewById(R.id.poster)
            val title: TextView = view.findViewById(R.id.title)
            val subtitle: TextView = view.findViewById(R.id.subtitle)
        }
    }
}
""",
    encoding="utf-8",
)
print("[ui] Recent/History list screen written")

graph = NAVGRAPH.read_text(encoding="utf-8")
if "@+id/navigation_recent" not in graph:
    entries = """
    <fragment
        android:id="@+id/navigation_recent"
        android:name="com.lagradost.cloudstream3.ui.library.LibraryListFragment">
        <argument
            android:name="mode"
            android:defaultValue="recent"
            app:argType="string" />
    </fragment>

    <fragment
        android:id="@+id/navigation_history"
        android:name="com.lagradost.cloudstream3.ui.library.LibraryListFragment">
        <argument
            android:name="mode"
            android:defaultValue="history"
            app:argType="string" />
    </fragment>
</navigation>
"""
    graph = graph.rstrip()
    if not graph.endswith("</navigation>"):
        sys.exit("[ui] navigation graph has no closing tag")
    graph = graph[: -len("</navigation>")] + entries
    NAVGRAPH.write_text(graph, encoding="utf-8")
    print("[ui] mobile_navigation.xml -> navigation_recent + navigation_history added")

lib_frag = LIB_FRAGMENT.read_text(encoding="utf-8")
if "navigation_recent" not in lib_frag:
    lib_frag = lib_frag.replace(
        'view.findViewById<View>(R.id.card_recent)?.setOnClickListener { toast("Recent: next step") }',
        'view.findViewById<View>(R.id.card_recent)?.setOnClickListener {\n'
        '            runCatching { nav.navigate(R.id.navigation_recent) }.onFailure { toast("Recent could not be opened") }\n'
        '        }',
        1,
    )
    lib_frag = lib_frag.replace(
        'view.findViewById<View>(R.id.card_history)?.setOnClickListener { toast("History: next step") }',
        'view.findViewById<View>(R.id.card_history)?.setOnClickListener {\n'
        '            runCatching { nav.navigate(R.id.navigation_history) }.onFailure { toast("History could not be opened") }\n'
        '        }',
        1,
    )
    LIB_FRAGMENT.write_text(lib_frag, encoding="utf-8")
    print("[ui] LibraryHomeFragment.kt -> Recent + History cards wired")

# ---------------------------------------------------------------- 7. Offline (local videos)
OFF_LAYOUT = ROOT / "app/src/main/res/layout/fragment_offline.xml"
OFF_PLAYER_LAYOUT = ROOT / "app/src/main/res/layout/fragment_offline_player.xml"
OFF_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/library/OfflineFragment.kt"
OFF_PLAYER = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/library/OfflinePlayerFragment.kt"

OFF_LAYOUT.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#141010"
    android:orientation="vertical"
    android:padding="14dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Offline"
        android:textColor="#F5EAE6"
        android:textSize="24sp"
        android:textStyle="bold" />

    <TextView
        android:id="@+id/offline_hint"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="6dp"
        android:text="Pick a folder on this phone and its videos will play here."
        android:textColor="#93A1AE"
        android:textSize="13sp" />

    <com.google.android.material.button.MaterialButton
        android:id="@+id/offline_pick"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:layout_marginTop="10dp"
        android:text="Choose folder" />

    <androidx.recyclerview.widget.RecyclerView
        android:id="@+id/list"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_marginTop="12dp"
        android:layout_weight="1"
        android:clipToPadding="false" />
</LinearLayout>
""",
    encoding="utf-8",
)

OFF_PLAYER_LAYOUT.write_text(
    """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#000000">

    <androidx.media3.ui.PlayerView
        android:id="@+id/player_view"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:keepScreenOn="true" />
</FrameLayout>
""",
    encoding="utf-8",
)

OFF_FRAGMENT.write_text(
    """package com.lagradost.cloudstream3.ui.library

import android.content.ContentResolver
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.DocumentsContract
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.NavHostFragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.lagradost.cloudstream3.R
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Prime Box offline library: pick a folder on the phone with the system picker (SAF), list the
 * videos inside it and play them in the built-in player.
 */
class OfflineFragment : Fragment() {

    private data class Video(val name: String, val uri: Uri, val size: Long)

    private val prefs by lazy {
        requireContext().getSharedPreferences("primebox_offline", Context.MODE_PRIVATE)
    }

    private val pickFolder = registerForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri == null) return@registerForActivityResult
        runCatching {
            requireContext().contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION
            )
        }
        prefs.edit().putString(KEY_TREE, uri.toString()).apply()
        scan(uri)
    }

    private lateinit var adapter: OfflineAdapter
    private lateinit var hint: TextView

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_offline, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        hint = view.findViewById(R.id.offline_hint)
        val list = view.findViewById<RecyclerView>(R.id.list)
        list.layoutManager = LinearLayoutManager(requireContext())
        adapter = OfflineAdapter { video -> play(video) }
        list.adapter = adapter

        view.findViewById<View>(R.id.offline_pick).setOnClickListener {
            runCatching { pickFolder.launch(null) }
        }

        val saved = prefs.getString(KEY_TREE, null)
        if (saved != null) {
            runCatching { scan(Uri.parse(saved)) }
        }
    }

    private fun scan(treeUri: Uri) {
        viewLifecycleOwner.lifecycleScope.launch {
            hint.text = "Scanning…"
            val videos = withContext(Dispatchers.IO) {
                runCatching { collect(requireContext().contentResolver, treeUri) }.getOrDefault(emptyList())
            }
            adapter.submit(videos)
            hint.text = if (videos.isEmpty()) {
                "No videos found in that folder. Pick another one."
            } else {
                videos.size.toString() + " video(s) found"
            }
        }
    }

    private fun collect(resolver: ContentResolver, treeUri: Uri): List<Video> {
        val out = mutableListOf<Video>()
        walk(resolver, treeUri, DocumentsContract.getTreeDocumentId(treeUri), out, 0)
        return out.sortedBy { it.name.lowercase() }
    }

    private fun walk(
        resolver: ContentResolver,
        treeUri: Uri,
        documentId: String,
        out: MutableList<Video>,
        depth: Int
    ) {
        if (depth > 8) return
        val children = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, documentId)
        val projection = arrayOf(
            DocumentsContract.Document.COLUMN_DOCUMENT_ID,
            DocumentsContract.Document.COLUMN_DISPLAY_NAME,
            DocumentsContract.Document.COLUMN_MIME_TYPE,
            DocumentsContract.Document.COLUMN_SIZE
        )
        resolver.query(children, projection, null, null, null)?.use { cursor ->
            while (cursor.moveToNext()) {
                val childId = cursor.getString(0)
                val name = cursor.getString(1) ?: "video"
                val mime = cursor.getString(2) ?: ""
                val size = cursor.getLong(3)
                if (mime == DocumentsContract.Document.MIME_TYPE_DIR) {
                    walk(resolver, treeUri, childId, out, depth + 1)
                } else if (mime.startsWith("video/") || VIDEO_EXT.any { name.lowercase().endsWith(it) }) {
                    out.add(
                        Video(
                            name,
                            DocumentsContract.buildDocumentUriUsingTree(treeUri, childId),
                            size
                        )
                    )
                }
            }
        }
    }

    private fun play(video: Video) {
        runCatching {
            NavHostFragment.findNavController(this).navigate(
                R.id.navigation_offline_player,
                Bundle().apply { putString("uri", video.uri.toString()) }
            )
        }
    }

    private class OfflineAdapter(private val onClick: (Video) -> Unit) :
        RecyclerView.Adapter<OfflineAdapter.Holder>() {
        private val items = mutableListOf<Video>()

        fun submit(list: List<Video>) {
            items.clear()
            items.addAll(list)
            notifyDataSetChanged()
        }

        override fun getItemCount(): Int = items.size

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): Holder =
            Holder(LayoutInflater.from(parent.context).inflate(R.layout.item_library_row, parent, false))

        override fun onBindViewHolder(holder: Holder, position: Int) {
            val video = items[position]
            holder.title.text = video.name
            holder.subtitle.text = formatSize(video.size)
            holder.itemView.setOnClickListener { onClick(video) }
        }

        private fun formatSize(bytes: Long): String = when {
            bytes <= 0L -> ""
            bytes >= 1024L * 1024L * 1024L -> String.format("%.1f GB", bytes / 1073741824.0)
            bytes >= 1024L * 1024L -> String.format("%.0f MB", bytes / 1048576.0)
            else -> String.format("%.0f KB", bytes / 1024.0)
        }

        class Holder(view: View) : RecyclerView.ViewHolder(view) {
            val title: TextView = view.findViewById(R.id.title)
            val subtitle: TextView = view.findViewById(R.id.subtitle)
        }
    }

    companion object {
        private const val KEY_TREE = "tree_uri"
        private val VIDEO_EXT = listOf(
            ".mp4", ".mkv", ".webm", ".avi", ".mov", ".m4v", ".3gp", ".ts", ".flv", ".wmv"
        )
    }
}
""",
    encoding="utf-8",
)

OFF_PLAYER.write_text(
    """package com.lagradost.cloudstream3.ui.library

import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import com.lagradost.cloudstream3.R

/** Plays a local video (content:// uri) picked from the Offline screen. */
class OfflinePlayerFragment : Fragment() {

    private var player: ExoPlayer? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View = inflater.inflate(R.layout.fragment_offline_player, container, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val raw = arguments?.getString("uri") ?: return
        runCatching {
            val exo = ExoPlayer.Builder(requireContext()).build()
            player = exo
            view.findViewById<PlayerView>(R.id.player_view).player = exo
            exo.setMediaItem(MediaItem.fromUri(Uri.parse(raw)))
            exo.prepare()
            exo.playWhenReady = true
        }
    }

    override fun onDestroyView() {
        runCatching {
            player?.stop()
            player?.release()
        }
        player = null
        super.onDestroyView()
    }
}
""",
    encoding="utf-8",
)
print("[ui] Offline screen + local player written")

graph = NAVGRAPH.read_text(encoding="utf-8")
if "@+id/navigation_offline" not in graph:
    graph = graph.rstrip()
    if not graph.endswith("</navigation>"):
        sys.exit("[ui] navigation graph has no closing tag")
    graph = graph[: -len("</navigation>")] + """
    <fragment
        android:id="@+id/navigation_offline"
        android:name="com.lagradost.cloudstream3.ui.library.OfflineFragment" />

    <fragment
        android:id="@+id/navigation_offline_player"
        android:name="com.lagradost.cloudstream3.ui.library.OfflinePlayerFragment">
        <argument
            android:name="uri"
            app:argType="string" />
    </fragment>
</navigation>
"""
    NAVGRAPH.write_text(graph, encoding="utf-8")
    print("[ui] mobile_navigation.xml -> offline destinations added")

lib_frag = LIB_FRAGMENT.read_text(encoding="utf-8")
if "navigation_offline" not in lib_frag:
    lib_frag = lib_frag.replace(
        'view.findViewById<View>(R.id.card_offline)?.setOnClickListener { toast("Offline: next step") }',
        'view.findViewById<View>(R.id.card_offline)?.setOnClickListener {\n'
        '            runCatching { nav.navigate(R.id.navigation_offline) }.onFailure { toast("Offline could not be opened") }\n'
        '        }',
        1,
    )
    LIB_FRAGMENT.write_text(lib_frag, encoding="utf-8")
    print("[ui] LibraryHomeFragment.kt -> Offline card wired")

# source of the floating nav bar, injected into the checkout at build time
NAVBAR_SOURCE = 'package com.lagradost.cloudstream3.ui.pb\n\nimport androidx.annotation.DrawableRes\nimport androidx.compose.animation.animateColorAsState\nimport androidx.compose.animation.core.Spring\nimport androidx.compose.animation.core.animateFloatAsState\nimport androidx.compose.animation.core.spring\nimport androidx.compose.foundation.background\nimport androidx.compose.foundation.interaction.MutableInteractionSource\nimport androidx.compose.foundation.interaction.collectIsPressedAsState\nimport androidx.compose.foundation.layout.Box\nimport androidx.compose.foundation.layout.BoxWithConstraints\nimport androidx.compose.foundation.layout.Row\nimport androidx.compose.foundation.layout.fillMaxHeight\nimport androidx.compose.foundation.layout.fillMaxWidth\nimport androidx.compose.foundation.layout.height\nimport androidx.compose.foundation.layout.offset\nimport androidx.compose.foundation.layout.padding\nimport androidx.compose.foundation.layout.size\nimport androidx.compose.foundation.layout.width\nimport androidx.compose.foundation.selection.selectable\nimport androidx.compose.foundation.shape.RoundedCornerShape\nimport androidx.compose.material3.Icon\nimport androidx.compose.material3.Surface\nimport androidx.compose.material3.Text\nimport androidx.compose.runtime.Composable\nimport androidx.compose.runtime.getValue\nimport androidx.compose.runtime.remember\nimport androidx.compose.ui.Alignment\nimport androidx.compose.ui.Modifier\nimport androidx.compose.ui.draw.clip\nimport androidx.compose.ui.draw.clipToBounds\nimport androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.graphics.SolidColor\nimport androidx.compose.ui.graphics.graphicsLayer\nimport androidx.compose.ui.graphics.vector.ImageVector\nimport androidx.compose.ui.graphics.vector.path\nimport androidx.compose.ui.platform.LocalDensity\nimport androidx.compose.ui.res.painterResource\nimport androidx.compose.ui.text.TextStyle\nimport androidx.compose.ui.text.font.FontWeight\nimport androidx.compose.ui.text.rememberTextMeasurer\nimport androidx.compose.ui.text.style.TextOverflow\nimport androidx.compose.ui.unit.dp\nimport androidx.compose.ui.unit.sp\nimport com.lagradost.cloudstream3.R\nimport kotlin.math.abs\nimport kotlin.math.floor\n\ndata class PbNavItem(\n    val label: String,\n    @DrawableRes val iconRes: Int = 0,\n    val vector: ImageVector? = null,\n)\n\n/** Profile icon, drawn here so no extra icon dependency is needed. */\nval PbPersonIcon: ImageVector = ImageVector.Builder(\n    name = "PbPerson",\n    defaultWidth = 24.dp,\n    defaultHeight = 24.dp,\n    viewportWidth = 24f,\n    viewportHeight = 24f,\n).path(fill = SolidColor(Color.White)) {\n    moveTo(12f, 12f)\n    curveTo(14.21f, 12f, 16f, 10.21f, 16f, 8f)\n    curveTo(16f, 5.79f, 14.21f, 4f, 12f, 4f)\n    curveTo(9.79f, 4f, 8f, 5.79f, 8f, 8f)\n    curveTo(8f, 10.21f, 9.79f, 12f, 12f, 12f)\n    close()\n    moveTo(12f, 14f)\n    curveTo(9.33f, 14f, 4f, 15.34f, 4f, 18f)\n    lineTo(4f, 20f)\n    lineTo(20f, 20f)\n    lineTo(20f, 18f)\n    curveTo(20f, 15.34f, 14.67f, 14f, 12f, 14f)\n    close()\n}.build()\n\n/** The three Prime Box tabs. */\nval PB_NAV_ITEMS = listOf(\n    PbNavItem("Home", iconRes = R.drawable.home_icon_filled_24),\n    PbNavItem("Library", iconRes = R.drawable.library_icon_filled),\n    PbNavItem("Me", vector = PbPersonIcon),\n)\n\n// Exactly the colours the Off app uses for its floating bar.\nprivate val BAR_BG = Color(0xFF272A31)\nprivate val PILL_BG = Color(0xFF783820)\nprivate val SELECTED_FG = Color(0xFFFFDBCF)\nprivate val UNSELECTED_FG = Color(0xFFC8C5D0)\nprivate val LABEL_STYLE = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold)\n\nprivate const val ICON_SLOT = 56f\nprivate const val LABEL_GAP = 8f\nprivate val PILL_HEIGHT = 44.dp\n\n/**\n * Floating, pill-shaped navigation bar with one spring-driven selection value.\n *\n * A single animated float (the fractional selection position) drives every slot width, the\n * label fade and the indicator, so the shift between two buttons is one continuous motion\n * instead of several animations that can drift apart.\n */\n@Composable\nfun PbNavBar(\n    selectedIndex: Int,\n    onSelect: (Int) -> Unit,\n    items: List<PbNavItem> = PB_NAV_ITEMS,\n    modifier: Modifier = Modifier\n) {\n    if (items.isEmpty()) return\n\n    val density = LocalDensity.current\n    val measurer = rememberTextMeasurer()\n    val labelWidths = items.map { item ->\n        with(density) { measurer.measure(item.label, LABEL_STYLE).size.width.toDp().value }\n    }\n\n    val safeSelected = selectedIndex.coerceIn(0, items.lastIndex)\n\n    val progress by animateFloatAsState(\n        targetValue = safeSelected.toFloat(),\n        animationSpec = spring(dampingRatio = 0.78f, stiffness = Spring.StiffnessMediumLow),\n        label = "pb-nav-progress"\n    )\n\n    val expand = items.indices.map { i -> (1f - abs(progress - i)).coerceIn(0f, 1f) }\n    val weights = items.indices.map { i ->\n        ICON_SLOT + (labelWidths[i] + LABEL_GAP) * expand[i]\n    }\n    val totalWeight = weights.sum().takeIf { it > 0f } ?: 1f\n\n    val lower = floor(progress).toInt().coerceIn(0, items.lastIndex)\n    val upper = (lower + 1).coerceAtMost(items.lastIndex)\n    val fraction = (progress - lower).coerceIn(0f, 1f)\n\n    Surface(\n        shape = RoundedCornerShape(30.dp),\n        color = BAR_BG,\n        tonalElevation = 8.dp,\n        shadowElevation = 14.dp,\n        modifier = modifier.fillMaxWidth()\n    ) {\n        BoxWithConstraints(\n            Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 8.dp),\n            contentAlignment = Alignment.CenterStart\n        ) {\n            val slotWidths = weights.map { maxWidth * (it / totalWeight) }\n            val before = slotWidths.take(lower).fold(0.dp) { acc, w -> acc + w }\n            val pillOffset = before + slotWidths[lower] * fraction\n            val pillWidth = slotWidths[lower] + (slotWidths[upper] - slotWidths[lower]) * fraction\n\n            Box(\n                Modifier\n                    .align(Alignment.CenterStart)\n                    .offset(x = pillOffset)\n                    .width(pillWidth)\n                    .height(PILL_HEIGHT)\n                    .clip(RoundedCornerShape(PILL_HEIGHT / 2))\n                    .background(PILL_BG)\n            )\n\n            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {\n                items.forEachIndexed { index, item ->\n                    val interaction = remember { MutableInteractionSource() }\n                    val pressed by interaction.collectIsPressedAsState()\n                    val selected = index == safeSelected\n                    val open = expand[index]\n\n                    val pressScale by animateFloatAsState(\n                        targetValue = if (pressed) 0.92f else 1f,\n                        animationSpec = spring(dampingRatio = 0.40f, stiffness = Spring.StiffnessHigh),\n                        label = "pb-nav-press-" + index\n                    )\n                    val content by animateColorAsState(\n                        targetValue = if (selected) SELECTED_FG else UNSELECTED_FG,\n                        animationSpec = spring(dampingRatio = 0.8f, stiffness = Spring.StiffnessMediumLow),\n                        label = "pb-nav-content-" + index\n                    )\n\n                    Row(\n                        Modifier\n                            .weight(weights[index])\n                            .height(PILL_HEIGHT)\n                            .clipToBounds()\n                            .graphicsLayer {\n                                scaleX = pressScale\n                                scaleY = pressScale\n                            }\n                            .selectable(\n                                selected = selected,\n                                interactionSource = interaction,\n                                indication = null\n                            ) { onSelect(index) },\n                        verticalAlignment = Alignment.CenterVertically\n                    ) {\n                        Box(\n                            Modifier.width(ICON_SLOT.dp).fillMaxHeight(),\n                            contentAlignment = Alignment.Center\n                        ) {\n                            if (item.vector != null) {\n                                Icon(\n                                    imageVector = item.vector,\n                                    contentDescription = item.label,\n                                    tint = content,\n                                    modifier = Modifier.size(22.dp)\n                                )\n                            } else {\n                                Icon(\n                                    painter = painterResource(item.iconRes),\n                                    contentDescription = item.label,\n                                    tint = content,\n                                    modifier = Modifier.size(22.dp)\n                                )\n                            }\n                        }\n                        Text(\n                            item.label,\n                            color = content,\n                            style = LABEL_STYLE,\n                            maxLines = 1,\n                            overflow = TextOverflow.Clip,\n                            modifier = Modifier.graphicsLayer {\n                                alpha = ((open - 0.3f) / 0.7f).coerceIn(0f, 1f)\n                                translationX = (1f - open) * 30f\n                            }\n                        )\n                    }\n                }\n            }\n        }\n    }\n}\n'
NAV_HELPER_SOURCE = '    private fun setupFloatingNavBar(navController: NavController) {\n        val composeView =\n            findViewById<androidx.compose.ui.platform.ComposeView>(R.id.pb_nav_bar) ?: return\n        val selected = androidx.compose.runtime.mutableStateOf(0)\n        val destinations = intArrayOf(\n            R.id.navigation_home,\n            R.id.navigation_library,\n            R.id.navigation_settings,\n        )\n        navController.addOnDestinationChangedListener { _, destination, _ ->\n            selected.value = when (destination.id) {\n                R.id.navigation_library -> 1\n                R.id.navigation_settings -> 2\n                else -> 0\n            }\n        }\n        composeView.setViewCompositionStrategy(\n            androidx.compose.ui.platform.ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed\n        )\n        composeView.setContent {\n            com.lagradost.cloudstream3.ui.pb.PbNavBar(\n                selectedIndex = selected.value,\n                onSelect = { index ->\n                    runCatching {\n                        navController.navigate(destinations[index.coerceIn(0, destinations.lastIndex)])\n                    }\n                }\n            )\n        }\n    }\n\n'

# ---------------------------------------------------------------- 8. floating nav bar
NAVBAR_KT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/pb/PbNavBar.kt"
ACTIVITY_LAYOUT = ROOT / "app/src/main/res/layout/activity_main.xml"

NAVBAR_KT.parent.mkdir(parents=True, exist_ok=True)
NAVBAR_KT.write_text(NAVBAR_SOURCE, encoding="utf-8")
print("[ui] PbNavBar.kt written (floating bar, spring animation)")

layout = ACTIVITY_LAYOUT.read_text(encoding="utf-8")

# hide the stock bottom navigation view
layout = layout.replace(
    '        <com.google.android.material.bottomnavigation.BottomNavigationView\n'
    '            android:id="@+id/nav_view"\n',
    '        <com.google.android.material.bottomnavigation.BottomNavigationView\n'
    '            android:id="@+id/nav_view"\n'
    '            android:visibility="gone"\n',
    1,
)

# leave room so list content is never hidden behind the floating bar
layout = layout.replace(
    '            android:id="@+id/nav_host_fragment"\n'
    '            android:name="androidx.navigation.fragment.NavHostFragment"\n'
    '            android:layout_width="0dp"\n'
    '            android:layout_height="0dp"\n',
    '            android:id="@+id/nav_host_fragment"\n'
    '            android:name="androidx.navigation.fragment.NavHostFragment"\n'
    '            android:layout_width="0dp"\n'
    '            android:layout_height="0dp"\n'
    '            android:layout_marginBottom="86dp"\n',
    1,
)

if "@+id/pb_nav_bar" not in layout:
    closer = "    </androidx.constraintlayout.widget.ConstraintLayout>"
    idx = layout.rfind(closer)
    if idx < 0:
        sys.exit("[ui] ConstraintLayout closing tag not found in activity_main.xml")
    compose_view = (
        '\n        <androidx.compose.ui.platform.ComposeView\n'
        '            android:id="@+id/pb_nav_bar"\n'
        '            android:layout_width="0dp"\n'
        '            android:layout_height="wrap_content"\n'
        '            android:layout_marginStart="18dp"\n'
        '            android:layout_marginEnd="18dp"\n'
        '            android:layout_marginBottom="18dp"\n'
        '            app:layout_constraintBottom_toBottomOf="parent"\n'
        '            app:layout_constraintEnd_toEndOf="parent"\n'
        '            app:layout_constraintStart_toStartOf="parent" />\n'
    )
    layout = layout[:idx] + compose_view + layout[idx:]

ACTIVITY_LAYOUT.write_text(layout, encoding="utf-8")
print("[ui] activity_main.xml -> floating ComposeView added, stock bar hidden")

# wire it up in MainActivity
activity = MAIN_ACTIVITY.read_text(encoding="utf-8")
if "setupFloatingNavBar" not in activity:
    anchor = "        val navController = navHostFragment.navController\n"
    if anchor not in activity:
        sys.exit("[ui] navController anchor not found in MainActivity.kt")
    activity = activity.replace(anchor, anchor + "\n        setupFloatingNavBar(navController)\n", 1)

    marker = "    private fun updateNavBar(destination: NavDestination) {"
    if marker not in activity:
        sys.exit("[ui] updateNavBar anchor not found in MainActivity.kt")
    activity = activity.replace(marker, NAV_HELPER_SOURCE + marker, 1)
    MAIN_ACTIVITY.write_text(activity, encoding="utf-8")
    print("[ui] MainActivity.kt -> floating nav bar wired to the NavController")

# ---------------------------------------------------------------- 9. white accents (no violet)
COLORS = ROOT / "app/src/main/res/values/colors.xml"
colors = COLORS.read_text(encoding="utf-8")
for name, value in (
    ("colorPrimary", "#FFFFFF"),
    ("colorPrimaryDark", "#1C1B1F"),
    ("colorAccent", "#FFFFFF"),
):
    colors, n = re.subn(
        r'<color name="' + name + r'">[^<]*</color>',
        '<color name="' + name + '">' + value + '</color>',
        colors,
    )
    if n != 1:
        sys.exit("[ui] colour " + name + " not found in values/colors.xml")
COLORS.write_text(colors, encoding="utf-8")
print("[ui] colors.xml -> white accents (violet/blue primary replaced)")

UPDATE_DIALOG_SOURCE = '<?xml version="1.0" encoding="utf-8"?>\n<com.google.android.material.card.MaterialCardView xmlns:android="http://schemas.android.com/apk/res/android"\n    xmlns:app="http://schemas.android.com/apk/res-auto"\n    android:layout_width="match_parent"\n    android:layout_height="match_parent"\n    app:cardBackgroundColor="#1C1B1F"\n    app:cardCornerRadius="28dp"\n    app:cardElevation="0dp">\n\n    <LinearLayout\n        android:layout_width="match_parent"\n        android:layout_height="wrap_content"\n        android:orientation="vertical"\n        android:padding="24dp">\n\n        <TextView\n            android:id="@+id/pb_update_title"\n            android:layout_width="match_parent"\n            android:layout_height="wrap_content"\n            android:text="Updating your experience"\n            android:textColor="#FFFFFF"\n            android:textSize="20sp"\n            android:textStyle="bold" />\n\n        <TextView\n            android:id="@+id/pb_update_subtitle"\n            android:layout_width="match_parent"\n            android:layout_height="wrap_content"\n            android:layout_marginTop="6dp"\n            android:text="Please wait while your extensions are set up."\n            android:textColor="#CAC4D0"\n            android:textSize="14sp" />\n\n        <com.google.android.material.progressindicator.LinearProgressIndicator\n            android:id="@+id/pb_update_progress"\n            android:layout_width="match_parent"\n            android:layout_height="wrap_content"\n            android:layout_marginTop="20dp"\n            android:indeterminate="false"\n            android:max="100"\n            app:indicatorColor="#FFFFFF"\n            app:trackColor="#49454F"\n            app:trackCornerRadius="6dp"\n            app:trackThickness="8dp" />\n\n        <TextView\n            android:id="@+id/pb_update_status"\n            android:layout_width="match_parent"\n            android:layout_height="wrap_content"\n            android:layout_marginTop="12dp"\n            android:text="Starting…"\n            android:textColor="#CAC4D0"\n            android:textSize="13sp" />\n    </LinearLayout>\n</com.google.android.material.card.MaterialCardView>\n'
PREINSTALLED_SOURCE = 'package com.lagradost.cloudstream3.ui.pb\n\nimport android.app.Activity\nimport android.app.Dialog\nimport android.content.Context\nimport android.graphics.Color\nimport android.graphics.drawable.ColorDrawable\nimport android.view.Gravity\nimport android.view.ViewGroup\nimport android.widget.TextView\nimport com.google.android.material.progressindicator.LinearProgressIndicator\nimport com.lagradost.cloudstream3.R\nimport com.lagradost.cloudstream3.plugins.PluginManager\nimport com.lagradost.cloudstream3.ui.settings.extensions.REPOSITORIES_KEY\nimport com.lagradost.cloudstream3.ui.settings.extensions.RepositoryData\nimport com.lagradost.cloudstream3.utils.DataStore.getKey\nimport com.lagradost.cloudstream3.utils.DataStore.setKey\nimport kotlinx.coroutines.CoroutineScope\nimport kotlinx.coroutines.Dispatchers\nimport kotlinx.coroutines.launch\n\n/**\n * Adds the Phisher extension repository and installs the ten bundled providers on first launch,\n * showing a half-screen Material 3 sheet with real progress while it happens.\n */\nobject PbPreinstalled {\n\n    const val REPO_URL =\n        "cloudstreamrepo://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/refs/heads/builds/repo.json"\n\n    private data class PrebuiltPlugin(\n        val internalName: String,\n        val url: String,\n        val hash: String,\n    )\n\n    private val PLUGINS = listOf(\n        PrebuiltPlugin(\n            "MovieBoxProvider",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/MovieBoxProvider.cs3",\n            "sha256-dcb537cef5f3dbec3e0792d690c4f4aabf4251cad1c79fdd3b1642e68fca3c5f",\n        ),\n        PrebuiltPlugin(\n            "AnimeDekhoProvider",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/AnimeDekhoProvider.cs3",\n            "sha256-4d418aaf48fc722ebd6f3ed7acff2d259ee1ba468b71b5424f795beda09f0677",\n        ),\n        PrebuiltPlugin(\n            "Animedubhindi",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/Animedubhindi.cs3",\n            "sha256-b48590ac51f0e59f1bee0ea8b514b7320677d6738cb6dde20beb95ba2c9ce572",\n        ),\n        PrebuiltPlugin(\n            "AllMovieLandProvider",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/AllMovieLandProvider.cs3",\n            "sha256-1282e16296bcb80dfe5c07e5aed8dda0ca4a744973abaa000ef0a3d714aa09d7",\n        ),\n        PrebuiltPlugin(\n            "AniVortex",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/AniVortex.cs3",\n            "sha256-5751039f0fbf4f2db6ec7974bbabc85f1801f05b15b968174f2823150d7fdfce",\n        ),\n        PrebuiltPlugin(\n            "Movies4u",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/Movies4u.cs3",\n            "sha256-cb3dff6df9912334b6230918b88cb3b2730e3b1f56bb5657c18a01bf8a3fc44a",\n        ),\n        PrebuiltPlugin(\n            "IStreamFlare",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/IStreamFlare.cs3",\n            "sha256-f850ff3abbba6cdc0d7b7f8f21d3ee805a9abd71e65c29d279884267955c8865",\n        ),\n        PrebuiltPlugin(\n            "Hindmoviez",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/Hindmoviez.cs3",\n            "sha256-19dc763a3506d86ab4750c8490a2e8a3f80e56c55e962c0620b06fe90a1b756a",\n        ),\n        PrebuiltPlugin(\n            "DudeFilms",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/DudeFilms.cs3",\n            "sha256-e7512f6b2913f4b449e547df8fb9569f58642ff3c59f2a8836da03dda947e39e",\n        ),\n        PrebuiltPlugin(\n            "Animesalt",\n            "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/builds/Animesalt.cs3",\n            "sha256-5d5c518dc7ff13066b1c155d661d4afde2ac4b24b1510b27fdd4fe2eac32e1f1",\n        )\n    )\n\n    private const val PREFS = "primebox_preinstalled"\n\n    fun seed(activity: Activity) {\n        val prefs = activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE)\n        if (prefs.getBoolean("done_v1", false)) return\n        prefs.edit().putBoolean("done_v1", true).apply()\n\n        val dialog = showSheet(activity)\n        val progress = dialog.findViewById<LinearProgressIndicator>(R.id.pb_update_progress)\n        val status = dialog.findViewById<TextView>(R.id.pb_update_status)\n        val subtitle = dialog.findViewById<TextView>(R.id.pb_update_subtitle)\n        progress.max = PLUGINS.size + 1\n\n        fun ui(block: () -> Unit) {\n            runCatching { activity.runOnUiThread(block) }\n        }\n\n        CoroutineScope(Dispatchers.IO).launch {\n            // 1. register the repository\n            ui {\n                status.text = "Adding extension repository…"\n                progress.setProgressCompat(1, true)\n            }\n            runCatching {\n                val existing = activity.getKey<Array<RepositoryData>>(REPOSITORIES_KEY) ?: emptyArray()\n                if (existing.none { it.url == REPO_URL }) {\n                    activity.setKey(\n                        REPOSITORIES_KEY,\n                        existing + RepositoryData("Phisher Extensions", REPO_URL)\n                    )\n                }\n            }\n\n            // 2. install every provider\n            var done = 1\n            var failed = 0\n            for (plugin in PLUGINS) {\n                ui {\n                    status.text = "Installing " + plugin.internalName + "…"\n                }\n                val ok = runCatching {\n                    PluginManager.downloadPlugin(\n                        activity,\n                        plugin.url,\n                        plugin.hash,\n                        plugin.internalName,\n                        REPO_URL,\n                        true,\n                    )\n                }.getOrDefault(false)\n                if (!ok) failed++\n                done++\n                val current = done\n                ui {\n                    progress.setProgressCompat(current, true)\n                    status.text = current.toString() + " / " + (PLUGINS.size + 1)\n                }\n            }\n\n            ui {\n                subtitle.text = if (failed == 0) {\n                    "All extensions are ready."\n                } else {\n                    (PLUGINS.size - failed).toString() + " of " + PLUGINS.size +\n                        " extensions installed. The rest can be added from Extensions."\n                }\n                status.text = "Done"\n            }\n            kotlinx.coroutines.delay(1200)\n            ui { runCatching { dialog.dismiss() } }\n        }\n    }\n\n    private fun showSheet(activity: Activity): Dialog {\n        val dialog = Dialog(activity)\n        runCatching {\n            dialog.setContentView(R.layout.pb_update_dialog)\n            dialog.setCancelable(false)\n            val height = (activity.resources.displayMetrics.heightPixels * 0.5).toInt()\n            dialog.window?.apply {\n                setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))\n                setLayout(ViewGroup.LayoutParams.MATCH_PARENT, height)\n                setGravity(Gravity.BOTTOM)\n            }\n            dialog.show()\n        }\n        return dialog\n    }\n}\n'

# ---------------------------------------------------------------- 10. pre-installed extensions
PREINSTALLED_KT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/pb/PbPreinstalled.kt"
PREINSTALLED_KT.parent.mkdir(parents=True, exist_ok=True)
PREINSTALLED_KT.write_text(PREINSTALLED_SOURCE, encoding="utf-8")
print("[ui] PbPreinstalled.kt written (repo + 10 providers)")

UPDATE_DIALOG_XML = ROOT / "app/src/main/res/layout/pb_update_dialog.xml"
UPDATE_DIALOG_XML.write_text(UPDATE_DIALOG_SOURCE, encoding="utf-8")
print("[ui] pb_update_dialog.xml written (half-screen M3 sheet)")


activity = MAIN_ACTIVITY.read_text(encoding="utf-8")
if "PbPreinstalled" not in activity:
    anchor = "        CommonActivity.init(this)\n"
    if anchor not in activity:
        sys.exit("[ui] CommonActivity.init anchor not found in MainActivity.kt")
    activity = activity.replace(
        anchor,
        anchor + "        com.lagradost.cloudstream3.ui.pb.PbPreinstalled.seed(this)\n",
        1,
    )
    MAIN_ACTIVITY.write_text(activity, encoding="utf-8")
    print("[ui] MainActivity.kt -> PbPreinstalled.seed(this) wired")

# ---------------------------------------------------------------- 11. search open animation
SEARCH_FRAGMENT = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/search/SearchFragment.kt"
search = SEARCH_FRAGMENT.read_text(encoding="utf-8")
if "MaterialSharedAxis" not in search:
    class_anchor = (
        "class SearchFragment : BaseFragment<FragmentSearchBinding>(\n"
        "    BaseFragment.BindingCreator.Bind(FragmentSearchBinding::bind)\n"
        ") {\n"
    )
    if class_anchor not in search:
        sys.exit("[ui] SearchFragment class header not found")
    override = (
        "\n"
        "    override fun onCreate(savedInstanceState: Bundle?) {\n"
        "        super.onCreate(savedInstanceState)\n"
        "        runCatching {\n"
        "            enterTransition = com.google.android.material.transition.MaterialSharedAxis(\n"
        "                com.google.android.material.transition.MaterialSharedAxis.Y, true\n"
        "            ).apply { duration = 320L }\n"
        "            returnTransition = com.google.android.material.transition.MaterialSharedAxis(\n"
        "                com.google.android.material.transition.MaterialSharedAxis.Y, false\n"
        "            ).apply { duration = 260L }\n"
        "        }\n"
        "    }\n"
    )
    search = search.replace(class_anchor, class_anchor + override, 1)
    SEARCH_FRAGMENT.write_text(search, encoding="utf-8")
    print("[ui] SearchFragment.kt -> shared-axis open/close animation")

# ---------------------------------------------------------------- 12. collapsing settings header
SETTINGS_SCREEN = ROOT / "app/src/main/java/com/lagradost/cloudstream3/ui/settings/SettingsFragmentScreen.kt"
settings = SETTINGS_SCREEN.read_text(encoding="utf-8")

if "pbCollapse" not in settings:
    # imports for the graphics layer used by the header animation
    if "import androidx.compose.ui.graphics.graphicsLayer" not in settings:
        anchor_import = "import androidx.compose.ui.Modifier\n"
        if anchor_import not in settings:
            sys.exit("[ui] Modifier import not found in SettingsFragmentScreen.kt")
        settings = settings.replace(
            anchor_import,
            anchor_import +
            "import androidx.compose.ui.graphics.TransformOrigin\n" +
            "import androidx.compose.ui.graphics.graphicsLayer\n",
            1,
        )

    # a little more room above the profile row
    old_spacer = (
        "                Spacer(modifier = Modifier.height(MaterialTheme.padding.small))\n"
        "\n"
        "                val default = DataStoreHelper.getDefaultAccount("
    )
    new_spacer = (
        "                Spacer(modifier = Modifier.height(MaterialTheme.padding.large))\n"
        "\n"
        "                // 0 = expanded, 1 = fully collapsed into the top bar\n"
        "                val pbCollapse = (outerListState.value.toFloat() / 220f).coerceIn(0f, 1f)\n"
        "\n"
        "                val default = DataStoreHelper.getDefaultAccount("
    )
    if old_spacer not in settings:
        sys.exit("[ui] settings header spacer anchor not found")
    settings = settings.replace(old_spacer, new_spacer, 1)

    old_row = (
        "                Row(\n"
        "                    modifier = Modifier\n"
        "                        .fillMaxSize()\n"
        "                        .focusOutline()\n"
    )
    new_row = (
        "                Row(\n"
        "                    modifier = Modifier\n"
        "                        .fillMaxWidth()\n"
        "                        .graphicsLayer {\n"
        "                            val s = 1f - 0.30f * pbCollapse\n"
        "                            scaleX = s\n"
        "                            scaleY = s\n"
        "                            transformOrigin = TransformOrigin(0f, 0.5f)\n"
        "                            translationX = -pbCollapse * 14f\n"
        "                        }\n"
        "                        .focusOutline()\n"
    )
    if old_row not in settings:
        sys.exit("[ui] settings header Row anchor not found")
    settings = settings.replace(old_row, new_row, 1)

    old_pad = (
        "                        .padding(\n"
        "                            vertical = MaterialTheme.padding.large,\n"
        "                            horizontal = MaterialTheme.padding.medium\n"
        "                        )\n"
        "                ) {\n"
    )
    new_pad = (
        "                        .padding(\n"
        "                            vertical = MaterialTheme.padding.large * (1f - pbCollapse) +\n"
        "                                MaterialTheme.padding.small * pbCollapse,\n"
        "                            horizontal = MaterialTheme.padding.medium\n"
        "                        )\n"
        "                ) {\n"
    )
    if old_pad not in settings:
        sys.exit("[ui] settings header padding anchor not found")
    settings = settings.replace(old_pad, new_pad, 1)

    SETTINGS_SCREEN.write_text(settings, encoding="utf-8")
    print("[ui] SettingsFragmentScreen.kt -> collapsing profile header")
