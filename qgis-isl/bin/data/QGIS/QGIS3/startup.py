# script that will run qsettings constraints when QGIS starts
# config file :   qgis_constrained_settings.yml
# cf  https://gitlab.com/Oslandia/qgis/qgis-constrained-settings

import codecs
import collections
import os
import re
import shutil
from configparser import ConfigParser
from pathlib import Path

import yaml
from PyQt5.QtCore import QSettings
from qgis.core import Qgis, QgsApplication, QgsSettings

PLUGINS_PATH = Path("to_be_defined")


def plugin_metadata_as_dict(path) -> dict:
    """Read plugin metadata.txt and returns it as a Python dict.

    Raises:
        IOError: if metadata.txt is not found

    Returns:
        dict: dict of dicts.
    """
    config = ConfigParser()
    if path.is_file():
        config.read(path.resolve(), encoding="UTF-8")
        return {s: dict(config.items(s)) for s in config.sections()}
    raise IOError(f"Plugin metadata.txt not found at: {path}")


def normalizeVersion(s):
    """remove possible prefix from given string and convert to uppercase"""
    prefixes = ["VERSION", "VER.", "VER", "V.", "V", "REVISION", "REV.", "REV", "R.", "R"]
    if not s:
        return str()
    s = str(s).upper()
    for i in prefixes:
        if s[: len(i)] == i:
            s = s.replace(i, "")
    s = s.strip()
    return s


# ------------------------------------------------------------------------ #
def classifyCharacter(c):
    """return 0 for delimiter, 1 for digit and 2 for alphabetic character"""
    if c in [".", "-", "_", " "]:
        return 0
    if c.isdigit():
        return 1
    else:
        return 2


# ------------------------------------------------------------------------ #
def chopString(s):
    """convert string to list of numbers and words"""
    l = [s[0]]
    for i in range(1, len(s)):
        if classifyCharacter(s[i]) == 0:
            pass
        elif classifyCharacter(s[i]) == classifyCharacter(s[i - 1]):
            l[len(l) - 1] += s[i]
        else:
            l += [s[i]]
    return l


# ------------------------------------------------------------------------ #
def compareElements(s1, s2):
    """compare two particular elements"""
    # check if the matter is easy solvable:
    if s1 == s2:
        return 0
    # try to compare as numeric values (but only if the first character is not 0):
    if s1 and s2 and s1.isnumeric() and s2.isnumeric() and s1[0] != "0" and s2[0] != "0":
        if float(s1) == float(s2):
            return 0
        elif float(s1) > float(s2):
            return 1
        else:
            return 2
    # if the strings aren't numeric or start from 0, compare them as a strings:
    # but first, set ALPHA < BETA < PREVIEW < RC < TRUNK < [NOTHING] < [ANYTHING_ELSE]
    if s1 not in ["ALPHA", "BETA", "PREVIEW", "RC", "TRUNK"]:
        s1 = "Z" + s1
    if s2 not in ["ALPHA", "BETA", "PREVIEW", "RC", "TRUNK"]:
        s2 = "Z" + s2
    # the final test:
    if s1 > s2:
        return 1
    else:
        return 2


# ------------------------------------------------------------------------ #
def compareVersions(a, b):
    """Compare two version numbers. Return 0 if a==b or error, 1 if a>b and 2 if b>a"""
    if not a or not b:
        return 0
    a = normalizeVersion(a)
    b = normalizeVersion(b)
    if a == b:
        return 0
    # convert the strings to lists
    v1 = chopString(a)
    v2 = chopString(b)
    # set the shorter string as a base
    l = len(v1)
    if l > len(v2):
        l = len(v2)
    # try to determine within the common length
    for i in range(l):
        if compareElements(v1[i], v2[i]):
            return compareElements(v1[i], v2[i])
    # if the lists are identical till the end of the shorther string, try to compare the odd tail
    # with the simple space (because the 'alpha', 'beta', 'preview' and 'rc' are LESS then nothing)
    if len(v1) > l:
        return compareElements(v1[l], " ")
    if len(v2) > l:
        return compareElements(" ", v2[l])
    # if everything else fails...
    if a > b:
        return 1
    else:
        return 2


def splitVersion(s):
    """split string into 2 or 3 numerical segments"""
    if not s or type(s) != str:
        return None
    l = str(s).split(".")
    for c in l:
        if not c.isnumeric():
            return None
        if int(c) > 99:
            return None
    if len(l) not in [2, 3]:
        return None
    return l


def isCompatible(curVer, minVer, maxVer):
    """Compare current QGIS version with qgisMinVersion and qgisMaxVersion"""

    if not minVer or not curVer or not maxVer:
        return False

    minVer = splitVersion(re.sub(r"[^0-9.]+", "", minVer))
    maxVer = splitVersion(re.sub(r"[^0-9.]+", "", maxVer))
    curVer = splitVersion(re.sub(r"[^0-9.]+", "", curVer))

    if not minVer or not curVer or not maxVer:
        return False

    if len(minVer) < 3:
        minVer += ["0"]

    if len(curVer) < 3:
        curVer += ["0"]

    if len(maxVer) < 3:
        maxVer += ["99"]

    minVer = "{:04n}{:04n}{:04n}".format(int(minVer[0]), int(minVer[1]), int(minVer[2]))
    maxVer = "{:04n}{:04n}{:04n}".format(int(maxVer[0]), int(maxVer[1]), int(maxVer[2]))
    curVer = "{:04n}{:04n}{:04n}".format(int(curVer[0]), int(curVer[1]), int(curVer[2]))

    return minVer <= curVer and maxVer >= curVer


def pyQgisVersion():
    """Return current QGIS version number as X.Y.Z for testing plugin compatibility.
    If Y = 99, bump up to (X+1.0.0), so e.g. 2.99 becomes 3.0.0
    This way QGIS X.99 is only compatible with plugins for the upcoming major release.
    """
    x, y, z = re.findall(r"^(\d*).(\d*).(\d*)", Qgis.QGIS_VERSION)[0]
    if y == "99":
        x = str(int(x) + 1)
        y = z = "0"
    return "{}.{}.{}".format(x, y, z)


def listPlugins(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]


def copyPlugin(src, dst, symlinks=False, ignore=None):
    if not dst.exists():
        os.mkdir(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def getPluginVersion(path):
    plugin_md = plugin_metadata_as_dict(path)
    return plugin_md.get("general").get("version")


def updatePlugins():
    if not PLUGINS_PATH.exists():
        return

    userPluginsDir = Path(QgsApplication.qgisSettingsDirPath()) / "python/plugins"
    if not userPluginsDir.exists():  #fresh new profile
        userPluginsDir.mkdir(parents=True, exist_ok=False)
    userPlugins = listPlugins(userPluginsDir)
    refPlugins = listPlugins(PLUGINS_PATH)

    userSettings = QSettings()

    for plugin in refPlugins:
        path_ref_plugin = PLUGINS_PATH / plugin
        path_user_plugin = userPluginsDir / plugin

        isNewPlugin = True

        if plugin in userPlugins:
            ref_plugin_md = plugin_metadata_as_dict(path_ref_plugin / "metadata.txt")
            user_plugin_md = plugin_metadata_as_dict(path_user_plugin / "metadata.txt")
            compare = compareVersions(
                ref_plugin_md.get("general").get("version"), user_plugin_md.get("general").get("version")
            )
            if compare == 1:
                shutil.rmtree(path_user_plugin, ignore_errors=True)
                isNewPlugin = False
            else:
                continue

        copyPlugin(path_ref_plugin, path_user_plugin)

        if isNewPlugin:
            userSettings.setValue("/PythonPlugins/" + plugin, True)


def main():
    application = QgsApplication.instance()
    applicationSettings = QgsSettings(application.organizationName(), application.applicationName())
    globalSettingsPath = Path(applicationSettings.globalSettingsPath())
    qgisConstrainedSettingsPath = Path(__file__).parent / "qgis_constrained_settings.yml"

    if not qgisConstrainedSettingsPath.is_file():
        print("No file named {}".format(qgisConstrainedSettingsPath))
        return

    print("Load constrained settings from {}".format(qgisConstrainedSettingsPath))
    with open(str(qgisConstrainedSettingsPath)) as f:
        constrainedSettings = yaml.safe_load(f)

    userSettings = QSettings()
    print("Process {}".format(userSettings.fileName()))

    propertiesToRemove = constrainedSettings.get("propertiesToRemove", {})
    for group, properties in propertiesToRemove.items():
        userSettings.beginGroup(group)
        if isinstance(properties, str):
            if properties == "*":
                userSettings.remove("")
        else:
            for prop in properties:
                userSettings.remove(prop)
        userSettings.endGroup()

    globalSettings = ConfigParser()
    with open(str(globalSettingsPath)) as f:
        globalSettings.read_file(f)

    propertiesToMerge = constrainedSettings.get("propertiesToMerge", {})
    for group, properties in propertiesToMerge.items():
        if not globalSettings.has_section(group):
            continue
        userSettings.beginGroup(group)
        for prop in properties:
            if not globalSettings.has_option(group, prop):
                continue
            userPropertyValues = userSettings.value(prop)
            if not userPropertyValues:
                continue
            if not isinstance(userPropertyValues, list):
                userPropertyValues = [userPropertyValues]
            globalPropertyValues = globalSettings.get(group, prop)
            globalPropertyValues = globalPropertyValues.split(",")
            # codecs.decode(v, "unicode_espace") is used to convert the raw string into a normal
            # string. This is required to avoid changing \\ sequences into \\\\ sequences
            globalPropertyValues = list(
                map(
                    lambda v: codecs.decode(v.strip('" '), "unicode_escape"),
                    globalPropertyValues,
                )
            )
            userPropertyValues = globalPropertyValues + userPropertyValues
            # remove duplicates
            userPropertyValues = list(collections.OrderedDict.fromkeys(userPropertyValues))
            userSettings.setValue(prop, userPropertyValues)
        userSettings.endGroup()

    propertyValuesToRemove = constrainedSettings.get("propertyValuesToRemove", {})
    for group, properties in propertyValuesToRemove.items():
        userSettings.beginGroup(group)
        for prop in properties:
            userPropertyValues = userSettings.value(prop)
            if not userPropertyValues:
                continue
            valuesToRemove = list(map(lambda v: v.rstrip("/\\ "), properties[prop]))
            userPropertyValues = [v for v in userPropertyValues if v.rstrip("/\\ ") not in valuesToRemove]
            userSettings.setValue(prop, userPropertyValues)
        userSettings.endGroup()


if __name__ == "startup":
    updatePlugins()
    main()
