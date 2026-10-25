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
