"""
LifeOS Desktop Tracker — App Classifier
Classifies a Windows process as 'productive', 'distracting', or 'neutral'
based on configurable lookup sets.

Classification priority:
  1. PRODUCTIVE_APPS — if matched → "productive"
  2. DISTRACTING_APPS — if matched → "distracting"
  3. NEUTRAL_APPS — if matched → "neutral"
  4. Default fallback → "unknown" (triggers AI)
"""

import json
import os
import atexit

# ── Productive Applications ───────────────────────────────────────────────────
# Code editors, IDEs, terminals, note-taking, and office productivity tools.
PRODUCTIVE_APPS: set[str] = {
    # Code Editors & IDEs
    "code.exe", "code - insiders.exe",
    "devenv.exe",                               # Visual Studio
    "idea64.exe", "pycharm64.exe", "webstorm64.exe",
    "clion64.exe", "rider64.exe", "goland64.exe",
    "datagrip64.exe", "rubymine64.exe", "phpstorm64.exe",
    "androidstudio64.exe",
    "eclipse.exe", "netbeans64.exe",
    "sublime_text.exe", "atom.exe", "notepad++.exe",
    "vim.exe", "nvim.exe", "emacs.exe",
    "cursor.exe", "zed.exe",

    # Terminals
    "wt.exe", "terminal.exe",
    "powershell.exe", "windowspowershell.exe",
    "cmd.exe",
    "bash.exe", "ubuntu.exe", "wsl.exe",
    "hyper.exe", "alacritty.exe", "mintty.exe",

    # Microsoft Office
    "winword.exe", "excel.exe", "powerpnt.exe",
    "onenote.exe", "msaccess.exe",

    # Design & Creative (work tools)
    "photoshop.exe", "illustrator.exe", "indesign.exe",
    "premierepro.exe", "afterfx.exe", "audition.exe",
    "xd.exe", "figma.exe", "sketch.exe",
    "blender.exe", "gimp-2.10.exe", "inkscape.exe",
    "davinci resolve.exe",

    # Development Utilities
    "postman.exe", "insomnia.exe",
    "docker desktop.exe",
    "github desktop.exe", "sourcetree.exe",
    "gitkraken.exe",
    "dbeaver.exe", "tableplus.exe",
    "sequel pro.exe", "mongodb compass.exe",
    "redis-desktop-manager.exe",

    # Note-taking & Knowledge Management
    "notion.exe", "obsidian.exe",
    "roamresearch.exe", "logseq.exe",

    # Task Management
    "todoist.exe", "trello.exe", "linear.exe",

    # Data & Databases
    "mysql.exe", "mysqld.exe", "pgadmin4.exe", "postgres.exe",
    "sqldeveloper.exe", "heidisql.exe", "sqlite3.exe", "ssms.exe",
    "azure data studio.exe",

    # Runtimes & CLIs
    "python.exe", "python3.exe", "node.exe", "java.exe",
    "jupyter-lab.exe", "jupyter-notebook.exe", "docker.exe",

    # Virtualization
    "vmware.exe", "virtualbox.exe", "vboxmanage.exe",

    # Other Dev Tools
    "wireshark.exe", "fiddler.exe", "charles.exe", "filezilla.exe",
    "winscp.exe", "putty.exe", "mobaxterm.exe",

    # ── Extended Dev & Tech ──
    "androidstudio.exe", "anaconda.exe", "spyder.exe", "rstudio.exe", "qtcreator.exe",
    "matlab.exe", "octave.exe", "codeblocks.exe", "xampp-control.exe", "wampmanager.exe",
    "nginx.exe", "apache.exe", "tomcat.exe", "mongo.exe", "mongod.exe",
    "deno.exe", "bun.exe", "rustc.exe", "cargo.exe", "gcc.exe",
    "g++.exe", "clang.exe", "cmake.exe", "make.exe", "dotnet.exe",
    "msvsmon.exe", "msbuild.exe", "nuget.exe", "composer.exe", "yarn.exe",
    "npm.exe", "pip.exe", "conda.exe", "virtualenv.exe", "poetry.exe",
    "vagrant.exe", "packer.exe", "terraform.exe", "ansible.exe", "puppet.exe",
    "chef.exe", "aws.exe", "az.exe", "gcloud.exe", "kubectl.exe",
    "minikube.exe", "helm.exe", "lens.exe", "k9s.exe", "istioctl.exe",
    "prometheus.exe", "grafana.exe", "kibana.exe", "logstash.exe", "filebeat.exe",
    "fluentd.exe", "splunk.exe", "datadog-agent.exe", "newrelic-infra.exe", "dynatrace.exe",
    "appdynamics.exe", "jira.exe", "confluence.exe", "bitbucket.exe", "gitlab.exe",
    "bamboo.exe", "jenkins.exe", "travis.exe", "circleci.exe", "teamcity.exe",
    "octopus.exe", "sonar-scanner.exe", "fortify.exe", "checkmarx.exe", "veracode.exe",
    "blackduck.exe", "snyk.exe", "whitesource.exe", "nexus.exe", "artifactory.exe",
    "jmeter.exe", "loadrunner.exe", "gatling.exe", "locust.exe", "selenium.exe",
    "cypress.exe", "playwright.exe", "puppeteer.exe", "appium.exe", "soapui.exe",
    "swagger.exe", "graphql.exe", "grpc.exe", "protoc.exe", "thrift.exe",
    
    # ── Extended Design & Creative ──
    "premiere.exe", "lightroom.exe", "coreldraw.exe", "maya.exe", "3dsmax.exe",
    "zbrush.exe", "cinema4d.exe", "houdini.exe", "nuke.exe", "mari.exe",
    "substancepainter.exe", "substancedesigner.exe", "marvelousdesigner.exe", "clo3d.exe", "keyshot.exe",
    "vray.exe", "arnold.exe", "renderman.exe", "redshift.exe", "octanerender.exe",
    "corona.exe", "lumion.exe", "twinmotion.exe", "enscape.exe", "unrealengine.exe",
    "unity.exe", "godot.exe", "cryengine.exe", "lumberyard.exe", "gamebuildergarage.exe",
    "rpgmaker.exe", "gamemaker.exe", "construct.exe", "stencyl.exe", "defold.exe",
}


# ── Distracting Applications ─────────────────────────────────────────────────
# Games, social media clients, streaming apps.
DISTRACTING_APPS: set[str] = {
    # Games
    "steam.exe",
    "epicgameslauncher.exe",
    "gog galaxy.exe",
    "battle.net.exe",
    "riotclientservices.exe",

    # Social Media / Messaging (personal)
    "discord.exe",
    "telegram.exe",
    "whatsapp.exe",
    "signal.exe",
    "skype.exe",

    # Streaming / Entertainment
    "spotify.exe", "spotifypremium.exe",
    "netflix.exe",
    "vlc.exe",
    "itunes.exe", "musicbee.exe", "winamp.exe",

    # More Games & Launchers
    "valorant.exe", "csgo.exe", "cs2.exe", "leagueclient.exe", "leagueoflegends.exe",
    "minecraft.exe", "minecraft.windows.exe", "roblox.exe", "robloxplayerbeta.exe",
    "genshinimpact.exe", "overwatch.exe", "gta5.exe", "r5apex.exe",
    "dota2.exe", "pubg.exe", "fallguys_client.exe",
    "origin.exe", "upc.exe", "eadestkop.exe",

    # More Social
    "viber.exe", "kakaotalk.exe", "line.exe", "wechat.exe", "tiktok.exe",

    # ── Extended Games ──
    "genshin.exe", "honkai.exe", "starrail.exe", "zenless.exe", "wuthering.exe",
    "toweroffantasy.exe", "pubg_lite.exe", "fortnite.exe", "fortniteclient-win64-shipping.exe", "apex.exe",
    "destiny2.exe", "warframe.exe", "warthunder.exe", "worldoftanks.exe", "worldofwarships.exe",
    "smite.exe", "paladins.exe", "brawlhalla.exe", "rocketleague.exe", "fallguys.exe",
    "amongus.exe", "phasmophobia.exe", "deadbydaylight.exe", "rainbowsix.exe", "r6.exe",
    "tarkov.exe", "rust.exe", "dayz.exe", "ark.exe", "conan.exe",
    "terraria.exe", "stardewvalley.exe", "civilization.exe", "civ6.exe", "hearts_of_iron_iv.exe",
    "europa_universalis_iv.exe", "crusader_kings_iii.exe", "stellaris.exe", "cities_skylines.exe", "sims4.exe",
    "ts4.exe", "gta-vc.exe", "gta-sa.exe", "rdr2.exe", "cyberpunk2077.exe",
    "witcher3.exe", "skyrim.exe", "fallout4.exe", "doom.exe", "doom_eternal.exe",
    "haloinfinite.exe", "mcc-win64-shipping.exe", "forzahorizon4.exe", "forzahorizon5.exe", "flightsimulator.exe",
    "msfs.exe", "xplane.exe", "p3d.exe", "dcs.exe", "il2.exe",
    "assetto.exe", "dirt.exe", "f1.exe", "needforspeed.exe", "fifa.exe",
    "pes.exe", "nba2k.exe", "madden.exe", "wwe2k.exe", "ufc.exe",
    "tekken.exe", "streetfighter.exe", "mortalkombat.exe", "soulcalibur.exe", "guiltygear.exe",

    # ── Extended Launchers & Media ──
    "ubisoftconnect.exe", "gog.exe", "rockstar.exe", "bethesda.exe", "blizzard.exe",
    "itch.exe", "amazon_games.exe", "xbox.exe", "xboxapp.exe", "gamepass.exe",
    "popcorntime.exe", "stremio.exe", "kodi.exe", "plex.exe", "emby.exe",
    "jellyfin.exe", "hulu.exe", "disneyplus.exe", "hbomax.exe", "primevideo.exe",
    "crunchyroll.exe", "funimation.exe", "twitch.exe", "youtube.exe", "youtube_music.exe",
    "soundcloud.exe", "tidal.exe", "deezer.exe", "qobuz.exe", "pandora.exe",
}


# ── Neutral Applications ──────────────────────────────────────────────────────
# Browsers are neutral here — the Chrome Extension handles fine-grained
# per-site classification. Tracking browsers at the OS level would create
# duplicate entries and inflate scores.
NEUTRAL_APPS: set[str] = {
    # Browsers (let the Chrome extension handle these)
    "chrome.exe", "msedge.exe", "firefox.exe",
    "brave.exe", "opera.exe", "vivaldi.exe",
    "safari.exe", "arc.exe",

    # Communication (work context)
    "teams.exe", "outlook.exe", "slack.exe", "zoom.exe",

    # System utilities
    "explorer.exe", "taskmgr.exe",
    "systemsettings.exe", "controlpanel.exe",
    "calc.exe", "mspaint.exe", "notepad.exe",
    "snippingtool.exe",

    # Remote Desktop & Other Utilities
    "anydesk.exe", "teamviewer.exe", "mstsc.exe",
    "wordpad.exe", "snagit.exe", "obs64.exe", "obs32.exe",
    "evernote.exe", "onedrive.exe", "googledrivesync.exe",
    "dropbox.exe", "box.exe",

    # ── Extended Utilities ──
    "winrar.exe", "7z.exe", "bandizip.exe", "peazip.exe", "winzip.exe",
    "rufus.exe", "balenaetcher.exe", "ventoy.exe", "hwmonitor.exe", "cpu-z.exe",
    "gpu-z.exe", "msiafterburner.exe", "riva_tuner.exe", "aida64.exe", "speccy.exe",
    "crystaldiskinfo.exe", "crystaldiskmark.exe", "as-ssd.exe", "atto.exe", "hdtune.exe",
    "prime95.exe", "cinebench.exe", "3dmark.exe", "pcmark.exe", "unigine.exe",
    "furmark.exe", "memtest.exe", "occt.exe", "hwinfo.exe", "hwinfo64.exe",
    "sysinternals.exe", "autoruns.exe", "procexp.exe", "procmon.exe", "tcpview.exe",
    "rammap.exe", "vmmap.exe", "desktops.exe", "bginfo.exe", "psping.exe",
    "psexec.exe", "pskill.exe", "pslist.exe", "psservice.exe", "pssuspend.exe",
    "psloglist.exe", "pspasswd.exe", "psloggedon.exe", "psgetsid.exe", "psfile.exe",
    
    # ── Extended Network / VPN ──
    "openvpn.exe", "wireguard.exe", "tailscale.exe", "zerotier.exe", "nordvpn.exe",
    "expressvpn.exe", "surfshark.exe", "cyberghost.exe", "pia.exe", "mullvad.exe",
    "protonvpn.exe", "windscribe.exe", "tunnelbear.exe", "hide.me.exe", "vyprvpn.exe",
    "ivpn.exe", "ovpn.exe", "perfectprivacy.exe", "airvpn.exe", "azirevpn.exe",
    "cryptostorm.exe", "blackvpn.exe", "bolehvpn.exe", "cactusvpn.exe", "ibvpn.exe",
    "safervpn.exe", "purevpn.exe", "zenmate.exe", "hotspotshield.exe", "betternet.exe",
    "touchvpn.exe", "hola.exe", "opera_vpn.exe", "warp.exe", "1.1.1.1.exe",
    "cloudflared.exe", "ngrok.exe", "localtunnel.exe", "serveo.exe", "pagekite.exe",
}


# ── Context-Aware Rules ───────────────────────────────────────────────────────
# Fine-grained categorization based on window title matching.
CONTEXT_RULES = {
    "discord.exe": [
        ("study", "productive"),
        ("homework", "productive"),
        ("work", "productive"),
    ],
    "chrome.exe": [
        ("youtube", "neutral"), # Example, though browser usually handled by extension
    ]
}


# ── AI Cache Persistence ──────────────────────────────────────────────────────
CACHE_FILE = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "POLARIS", "ai_cache.json")

def load_cache() -> dict[str, str]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache():
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(dynamic_cache, f)
    except Exception:
        pass

dynamic_cache: dict[str, str] = load_cache()
atexit.register(save_cache)


def classify(exe_name: str, window_title: str = "") -> str:
    """
    Classify a Windows process as 'productive', 'distracting', or 'neutral'.

    Args:
        exe_name: Raw process name, e.g. "code.exe" (case-insensitive).
        window_title: Window title for context-aware rules.

    Returns:
        One of: "productive" | "distracting" | "neutral" | "unknown"
    """
    normalized_exe = exe_name.strip().lower()
    normalized_title = window_title.strip().lower()

    # 1. Context-Aware Override
    if normalized_exe in CONTEXT_RULES:
        for keyword, category in CONTEXT_RULES[normalized_exe]:
            if keyword in normalized_title:
                return category

    # 2. Static Lists
    if normalized_exe in PRODUCTIVE_APPS:
        return "productive"
    if normalized_exe in DISTRACTING_APPS:
        return "distracting"
    if normalized_exe in NEUTRAL_APPS:
        return "neutral"
        
    # 3. Persistent AI Cache
    if normalized_exe in dynamic_cache:
        return dynamic_cache[normalized_exe]

    # Unknown apps return 'unknown' so main.py can resolve them via NLP API
    return "unknown"


def is_browser(exe_name: str) -> bool:
    """
    Returns True if the process is a web browser.
    Used to skip desktop tracking when the Chrome extension already handles it.
    """
    browsers = {
        "chrome.exe", "msedge.exe", "firefox.exe",
        "brave.exe", "opera.exe", "vivaldi.exe",
        "safari.exe", "arc.exe",
    }
    return exe_name.strip().lower() in browsers
