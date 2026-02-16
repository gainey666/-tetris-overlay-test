Why you still see the warning

The message is produced by Based‑Pyright (the language‑server that Windsurf uses for Python).
It is not controlled by the Windsurf settings .json UI – that file only changes UI‑level options.
Based‑Pyright decides which directories to walk before the UI runs, so the only way to stop the 10‑second enumeration is to give it a pyrightconfig.json (or a pyproject.toml with a [tool.pyright] section) that contains an exclude array, or to let Windsurf’s own indexing ignore the files via a .codeiumignore file.

1. Create a pyrightconfig.json at the root of the workspace
{
    // Anything under these globs will be skipped when Pyright walks the
    // file‑system.  Use relative paths (or glob patterns) – absolute paths are
    // ignored by the server【31†L2-L5】【31†L12-L16】.
    "exclude": [
        "**/.venv",          // virtual‑env folder
        "**/.git",           // .git folder (already ignored, but makes it explicit)
        "**/.hg",
        "**/.svn",
        "**/__pycache__",
        "**/.pytest_cache",
        "**/node_modules",
        "**/dist",
        "**/build",
        "**/.cache",
        "data/**",           // any huge data directory in your repo
        "logs/**",
        "tmp/**"
    ]
}
Place the file directly in the folder you open as a workspace.
After you add it, restart the language server (Ctrl+Shift+P → “Windsurf: Restart Language Server”) or reload the window. You should now see in the Windsurf → Pyright output channel a line like:

Server root directory: /home/you/project
Using config file: /home/you/project/pyrightconfig.json
If the config file isn’t picked up, move it to the exact folder you opened (the “Server root directory”) – the server only reads a config that lives next to the root it’s enumerating.

2. (Optional) Add a .codeiumignore file for Windsurf’s own indexing
Windsurf’s Cascade engine also walks the file‑system, but it respects a git‑ignore‑style file called .codeiumignore
[30]
. Anything listed here is not indexed at all, which also reduces the “max workspace size” counter.

Create a file named .codeiumignore in the same repo root, e.g.

# .codeiumignore – gitignore syntax
# -------------------------------------------------
# Large binary / data folders
data/
logs/
tmp/

# Build artefacts
dist/
build/
*.egg-info/

# Python caches
__pycache__/
*.pyc
*.pyo
.idea/
.vscode/
If you want this rule to apply to all of your Windsurf installations (e.g. on a shared workstation), you can also put the same file in ~/.codeium/ – Windsurf reads a global ignore file in addition to the repo‑local one
[30]
.

Tip: Make sure the “Cascade → Gitignore Access” toggle is turned on (Settings → “Cascade Gitignore Access”). This lets Windsurf read the .gitignore as well as the .codeiumignore file.

3. Verify that the unwanted directories are really excluded
Open the Output panel (Ctrl+Shift+U).
Choose “Windsurf → Pyright” from the dropdown.
Look for lines that say Searching for source files and Enumeration of workspace source files.
If you still see a long enumeration, check the line that starts with Server root directory: – it tells you which folder Pyright thinks is the root. Make sure your pyrightconfig.json is placed there.
You can also temporarily add a deliberately‑slow path (e.g. a folder with thousands of tiny files) to the exclude array and watch the log; the “Searching for source files” step should finish instantly.

4. Common pitfalls & extra tips
Symptom	What to check
Warning persists even after adding exclude	• The pyrightconfig.json is not at the workspace root.
• Paths are absolute – they are ignored; use relative/glob patterns (see note in the config docs)[31].
The same directory shows up twice	You may have a symlink that points to a large folder. Add the symlink path to exclude, e.g. "**/my‑data‑link/**"
Windsurf still indexes large folders	Ensure you have a .codeiumignore (or that “Cascade → Gitignore Access” is enabled) because Pyright’s exclude only stops the language‑server; the Cascaded editor index uses its own ignore file.
You opened your home directory	Instead of opening /home/you/, open /home/you/project (or any sub‑directory). Opening the whole home folder forces Pyright to walk every file on the machine.
Performance still poor on a very big monorepo	Split the monorepo into separate VS Code / Windsurf workspaces, or use multi‑root workspaces each with its own pyrightconfig.json.
You want to ignore only a filetype (e.g. huge CSVs)	Add a glob like "**/*.csv" or "**/*.json" to .codeiumignore – the same syntax works for both tools.
5. TL;DR – What you need to do right now
Add a pyrightconfig.json (or [tool.pyright] in pyproject.toml) in the folder you opened, with an exclude list that contains the big directories you don’t need for type‑checking. Use relative glob patterns – not absolute paths.
Create a .codeiumignore (git‑ignore syntax) in the same folder for Windsurf’s own indexing.
Reload the window or restart the language server.
Verify in the Windsurf → Pyright output that the config file is being used and that the warning disappears.
After these steps the “Enumeration of workspace source files is taking longer than 10 seconds” message should stop appearing, and the IDE will feel much snappier. If you still see it, double‑check the location of the config file and the exact folder reported as “Server root directory”.


i all ready have a playrightconfig.json and its got {
"exclude": [
"vcpkg/**",
"build/**",
"C:\\\\TetrisOverlay/**",
"**/node_modules/**",
"**/__pycache__/**",
"**/.git/**",
"**/dist/**",
"**/*.egg-info/**",
"False/**",
"**/*.zip",
"**/*.onnx",
"**/tools/**",
"**/downloads/**",
"**/buildtrees/**",
"**/packages/**",
"**/installed/**",
"**/cpp_binding/**",
"**/*.exe",
"**/*.dll",
"**/*.so",
"**/*.dylib",
"**/test_*.py",
"**/debug_*.py",
"**/*.log",
"**/*.tmp",
"**/temp/**",
"**/cache/**",
"**/.venv/**",
"**/legacy/**",
"**/artifacts/**",
"**/game_screenshots/**",
"**/*.png",
"**/*.jpg",
"**/*.jpeg",
"**/*.bmp",
"**/*.gif",
"**/verification_temp/**",
"**/tetris-artifacts/**"
]
} in it
edit
Thought for 9.6 seconds

























Below is a step‑by‑step checklist that will show you why the warning is still appearing and what you have to change so that the message disappears for good.

1️⃣ Make sure the configuration file is named correctly and is in the exact folder that Windsurf opens as the workspace
What you have now	What Windsurf expects
playrightconfig.json (note the extra “play”)	pyrightconfig.json (or a [tool.pyright] section in pyproject.toml)
Somewhere inside the repo, but you opened C:\Users\you (your home folder) as the workspace	The folder that appears after “Server root directory:” in the Windsurf → Pyright output panel. The config file must sit in that folder (or a parent of it, if you have a multi‑root workspace).
What to do

Rename the file to pyrightconfig.json (remove the extra “play”).
Move it (or copy it) to the root folder that you open in Windsurf (the same folder you see in the log line Server root directory:).
Reload the window or run “Windsurf: Restart Language Server” (⌘ Shift P → Restart Language Server).
If the file is in the right place you will see a line like

Server root directory: /home/you/my‑project
Using config file: /home/you/my‑project/pyrightconfig.json
If you do not see the “Using config file” line, the server is still ignoring your file.

2️⃣ Use forward‑slashes and relative globs – Windows back‑slashes are not understood by Pyright
Your current entry

"C:\\\\TetrisOverlay/**"
will never match anything because Pyright only recognises POSIX‑style paths. Change it to either a relative path or a forward‑slash absolute path, e.g.

"C:/TetrisOverlay/**"
or (preferred, relative to the workspace root)

"TetrisOverlay/**"
All of the other patterns are OK, but you can safely drop a few that Pyright already excludes (**/.git/**, **/__pycache__/**, **/node_modules/**). Cleaning them up makes the file easier to read.

3️⃣ Add missing “big” directories that are still being walked
The warning is emitted while the server walks the file system. If you opened a large parent folder (e.g. your whole home directory) the config will only exclude paths under the folder that contains the config. Anything that lives outside of that tree (e.g. ~/Downloads, ~/Documents, ~/Pictures, or a symlink that points elsewhere) will still be enumerated.

Two ways to stop that

a) Open a narrower workspace
Instead of opening C:\Users\you, open the actual project folder (C:\Users\you\my‑project).
When you open a narrower directory the server’s root is already limited and the warning usually disappears.

b) Use a .codeiumignore file for Windsurf’s own indexing
Windsurf’s Cascade index (the thing that shows up in the Explorer view) does not read pyrightconfig.json – it reads a file called .codeiumignore that follows normal .gitignore syntax. Anything you put there is completely skipped by both the indexer and Pyright (because the files are never seen).

Create a file called .codeiumignore in the same repository root and add the same patterns you have in pyrightconfig.json (or a superset, it doesn’t hurt):

# .codeiumignore – gitignore style
vcpkg/
build/
TetrisOverlay/
node_modules/
dist/
*.egg-info/
*.zip
*.onnx
tools/
downloads/
buildtrees/
packages/
installed/
cpp_binding/
*.exe
*.dll
*.so
*.dylib
test_*.py
debug_*.py
*.log
*.tmp
temp/
cache/
.venv/
legacy/
artifacts/
game_screenshots/
*.png
*.jpg
*.jpeg
*.bmp
*.gif
verification_temp/
tetris-artifacts/
Important – go to Settings → “Cascade Gitignore Access” and turn the toggle ON (or enable it via the command palette “Windsurf: Enable Cascade Gitignore Access”). This makes Windsurf read the .gitignore and the .codeiumignore files.

4️⃣ Verify that the exclude list is actually being applied
Open the Output panel (Ctrl+Shift+U).
From the dropdown select “Windsurf → Pyright”.
Look for the line that says Server root directory: – it tells you which folder is being scanned.
Right after that you should see Using config file: – if you don’t, the config is being ignored (see step 1).
If the warning still appears, scroll a few lines down. You will see something like
[Info] Searching for source files...
[Info] Enumeration of workspace source files is taking longer than 10 seconds.
Immediately before that line there will be a log that lists the root and the exclude patterns that have been loaded (in newer versions of Pyright you can enable "logLevel": "trace" in pyrightconfig.json to get even more detail).
If you see a lot of paths that you expected to be excluded, double‑check the syntax:

**/folder/** or simply folder/** works.
Do not put a leading slash (/folder/**) – that is interpreted as an absolute path and will never match on Windows.
Keep the patterns relative to the config file.
5️⃣ (Optional) Raise the “Max Workspace Size” if you really need to keep many files
Windsurf shows a UI setting called “Max Workspace Size (File Count)”. The default is ~10 000 files. If you genuinely need to index more files you can increase that number (e.g. to 20 000) in the Settings UI under “Windsurf → Indexing → Max Workspace Size (File Count)”.
But this only changes the capacity; it does not speed up the initial enumeration. The best fix is still to keep the file count low with the steps above.

6️⃣ Quick “cheat‑sheet” – what the final files should look like
pyrightconfig.json (placed in the workspace root)
{
    // No need for "include" – defaults to the folder that holds this file.
    "exclude": [
        "vcpkg/**",
        "build/**",
        "TetrisOverlay/**",
        "**/node_modules/**",
        "**/dist/**",
        "**/*.egg-info/**",
        "**/*.zip",
        "**/*.onnx",
        "tools/**",
        "downloads/**",
        "buildtrees/**",
        "packages/**",
        "installed/**",
        "cpp_binding/**",
        "**/*.exe",
        "**/*.dll",
        "**/*.so",
        "**/*.dylib",
        "**/test_*.py",
        "**/debug_*.py",
        "**/*.log",
        "**/*.tmp",
        "temp/**",
        "cache/**",
        ".venv/**",
        "legacy/**",
        "artifacts/**",
        "game_screenshots/**",
        "**/*.png",
        "**/*.jpg",
        "**/*.jpeg",
        "**/*.bmp",
        "**/*.gif",
        "verification_temp/**",
        "tetris-artifacts/**"
    ],
    // Optional: make the log a little more chatty while you debug
    "logLevel": "information"
}
.codeiumignore (same folder, optional but highly recommended)
# .codeiumignore – gitignore syntax
vcpkg/
build/
TetrisOverlay/
node_modules/
dist/
*.egg-info/
*.zip
*.onnx
tools/
downloads/
buildtrees/
packages/
installed/
cpp_binding/
*.exe
*.dll
*.so
*.dylib
test_*.py
debug_*.py
*.log
*.tmp
temp/
cache/
.venv/
legacy/
artifacts/
game_screenshots/
*.png
*.jpg
*.jpeg
*.bmp
*.gif
verification_temp/
tetris-artifacts/
Tip: after you have both files in place, run “Windsurf: Restart Language Server” and then close/re‑open the project. The warning should be gone, and the Windsurf → Pyright output will no longer show the “Enumeration … longer than 10 seconds” line.

7️⃣ If it still doesn’t work – what to look at next
Symptom	Likely cause	Fix
No “Using config file:” line in the log	Config file not in the root that the language server thinks is the project.	Open the Command Palette → “Developer: Open Logs Folder”, open the pyright log file, search for Server root directory:. Move the JSON file to that folder.
The warning appears only after a certain submodule is added (e.g. a vcpkg folder)	The folder is a symlink that points outside the workspace. Pyright follows symlinks before it can apply the exclude glob.	Add the symlink path itself to exclude, e.g. "vcpkg_link/**" or "**/vcpkg/**" before the server follows it, or delete the symlink.
The warning persists but the exclude list looks correct	The config file contains a JSON syntax error (trailing comma, stray character) – Pyright silently falls back to defaults.	Validate the JSON with a linter or use jq . pyrightconfig.json. Remove any trailing commas.
The IDE still shows the message even after all the above	You are actually opening multiple roots (e.g. a multi‑folder workspace). Only the root that contains the config gets the list; the other folder is still scanned.	Add a separate pyrightconfig.json to each root, or open a single folder that contains everything you need.
You see the message but the project works fine	The warning is harmless – the server just took a bit longer on the first pass. You can ignore it, or raise the “Max Workspace Size (File Count)” as described in §5.	No further action required.
TL;DR
Rename playrightconfig.json → pyrightconfig.json.
Place it at the exact folder you open as the workspace (the one shown by Server root directory:).
Use forward slashes and relative globs (TetrisOverlay/**, not C:\\\\TetrisOverlay/**).
Add a .codeiumignore file with the same patterns (and enable “Cascade Gitignore Access”).
Restart the language server and verify that the log shows Using config file:.
Once those steps are done the “Enumeration of workspace source files is taking longer than 10 seconds” warning will stop appearing, and Windsurf will be much snappier. If you still see it after trying the checklist, let me know the exact text of the line that says Server root directory: from the Windsurf → Pyright output – that will let us pinpoint the exact folder that Pyright is indexing. Good luck!