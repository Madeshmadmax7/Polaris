"""
LifeOS Desktop Tracker — App Name Resolver
Maps raw Windows process names (EXE) to human-friendly application names.
If an EXE is not in the lookup table, the raw process name is returned as fallback.
"""

# ── EXE → Friendly Name ──────────────────────────────────────────────────────
EXE_TO_APP_NAME: dict[str, str] = {
    # Code Editors & IDEs
    "code.exe":               "Visual Studio Code",
    "code - insiders.exe":    "VS Code Insiders",
    "devenv.exe":             "Visual Studio",
    "idea64.exe":             "IntelliJ IDEA",
    "pycharm64.exe":          "PyCharm",
    "webstorm64.exe":         "WebStorm",
    "clion64.exe":            "CLion",
    "rider64.exe":            "Rider",
    "goland64.exe":           "GoLand",
    "datagrip64.exe":         "DataGrip",
    "rubymine64.exe":         "RubyMine",
    "phpstorm64.exe":         "PhpStorm",
    "androidstudio64.exe":    "Android Studio",
    "eclipse.exe":            "Eclipse IDE",
    "netbeans64.exe":         "NetBeans",
    "sublime_text.exe":       "Sublime Text",
    "atom.exe":               "Atom",
    "notepad++.exe":          "Notepad++",
    "vim.exe":                "Vim",
    "nvim.exe":               "Neovim",
    "emacs.exe":              "Emacs",
    "cursor.exe":             "Cursor",
    "zed.exe":                "Zed",

    # Terminals
    "wt.exe":                 "Windows Terminal",
    "terminal.exe":           "Terminal",
    "powershell.exe":         "PowerShell",
    "windowspowershell.exe":  "Windows PowerShell",
    "cmd.exe":                "Command Prompt",
    "bash.exe":               "Bash",
    "ubuntu.exe":             "Ubuntu (WSL)",
    "wsl.exe":                "WSL",
    "hyper.exe":              "Hyper Terminal",
    "alacritty.exe":          "Alacritty",
    "mintty.exe":             "MinTTY (Git Bash)",

    # Microsoft Office
    "winword.exe":            "Microsoft Word",
    "excel.exe":              "Microsoft Excel",
    "powerpnt.exe":           "Microsoft PowerPoint",
    "onenote.exe":            "Microsoft OneNote",
    "outlook.exe":            "Microsoft Outlook",
    "msaccess.exe":           "Microsoft Access",
    "mspub.exe":              "Microsoft Publisher",
    "teams.exe":              "Microsoft Teams",

    # Design & Creative
    "photoshop.exe":          "Adobe Photoshop",
    "illustrator.exe":        "Adobe Illustrator",
    "indesign.exe":           "Adobe InDesign",
    "premierepro.exe":        "Adobe Premiere Pro",
    "afterfx.exe":            "Adobe After Effects",
    "audition.exe":           "Adobe Audition",
    "xd.exe":                 "Adobe XD",
    "figma.exe":              "Figma",
    "sketch.exe":             "Sketch",
    "blender.exe":            "Blender",
    "gimp-2.10.exe":          "GIMP",
    "inkscape.exe":           "Inkscape",
    "davinci resolve.exe":    "DaVinci Resolve",

    # Development Tools
    "postman.exe":            "Postman",
    "insomnia.exe":           "Insomnia",
    "docker desktop.exe":     "Docker Desktop",
    "github desktop.exe":     "GitHub Desktop",
    "sourcetree.exe":         "Sourcetree",
    "gitkraken.exe":          "GitKraken",
    "dbeaver.exe":            "DBeaver",
    "tableplus.exe":          "TablePlus",
    "sequel pro.exe":         "Sequel Pro",
    "mongodb compass.exe":    "MongoDB Compass",
    "redis-desktop-manager.exe": "Redis Desktop Manager",

    # Productivity & Notes
    "notion.exe":             "Notion",
    "obsidian.exe":           "Obsidian",
    "roamresearch.exe":       "Roam Research",
    "logseq.exe":             "Logseq",
    "todoist.exe":            "Todoist",
    "trello.exe":             "Trello",
    "linear.exe":             "Linear",
    "slack.exe":              "Slack",
    "zoom.exe":               "Zoom",
    "discord.exe":            "Discord",
    "telegram.exe":           "Telegram",
    "whatsapp.exe":           "WhatsApp",
    "signal.exe":             "Signal",
    "skype.exe":              "Skype",

    # Browsers (neutral — extension handles these)
    "chrome.exe":             "Google Chrome",
    "msedge.exe":             "Microsoft Edge",
    "firefox.exe":            "Firefox",
    "brave.exe":              "Brave Browser",
    "opera.exe":              "Opera",
    "vivaldi.exe":            "Vivaldi",
    "safari.exe":             "Safari",
    "arc.exe":                "Arc Browser",

    # Media & Entertainment
    "vlc.exe":                "VLC Media Player",
    "spotify.exe":            "Spotify",
    "spotifypremium.exe":     "Spotify",
    "itunes.exe":             "iTunes",
    "musicbee.exe":           "MusicBee",
    "winamp.exe":             "Winamp",

    # Games & Distractions
    "steam.exe":              "Steam",
    "epicgameslauncher.exe":  "Epic Games Launcher",
    "gog galaxy.exe":         "GOG Galaxy",
    "battle.net.exe":         "Battle.net",
    "riotclientservices.exe": "Riot Games Client",

    # System
    "explorer.exe":           "Windows Explorer",
    "taskmgr.exe":            "Task Manager",
    "systemsettings.exe":     "Windows Settings",
    "controlpanel.exe":       "Control Panel",
    "calc.exe":               "Calculator",
    "mspaint.exe":            "Microsoft Paint",
    "notepad.exe":            "Notepad",
    "snippingtool.exe":       "Snipping Tool",
}


def resolve(exe_name: str) -> str:
    """
    Resolve a Windows process EXE name to a friendly application name.

    Args:
        exe_name: Raw process name, e.g. "code.exe" or "WINWORD.EXE"

    Returns:
        Friendly name like "Visual Studio Code", or the raw exe_name if unknown.
    """
    if not exe_name:
        return "Unknown"
    normalized = exe_name.strip().lower()
    return EXE_TO_APP_NAME.get(normalized, exe_name)
