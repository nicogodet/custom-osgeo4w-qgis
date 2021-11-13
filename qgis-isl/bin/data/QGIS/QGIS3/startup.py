# script that will run qsettings constraints when QGIS starts
# config file :   qgis_constrained_settings.yml
# cf  https://gitlab.com/Oslandia/qgis/qgis-constrained-settings

import codecs
import collections
import configparser
import os
import shutil
from configparser import ConfigParser
from pathlib import Path

import yaml
from PyQt5.QtCore import QSettings
from qgis.core import QgsApplication, QgsSettings
from qgis.utils import loadPlugin, reloadPlugin, startPlugin, unloadPlugin

from .version_compare import compareVersions

PLUGINS_PATH = ""


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


def listPlugins(path):
    return [f.name for f in os.scandir(path) if f.is_dir()]


def copyPlugin(src, dst, symlinks=False, ignore=None):
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
    userPluginsDir = Path(QgsApplication.qgisSettingsDirPath()) / "python/plugins"
    userPlugins = listPlugins(Path(QgsApplication.qgisSettingsDirPath() / "python/plugins"))
    refPlugins = listPlugins(Path(PLUGINS_PATH))

    for plugin in refPlugins:
        path_ref_plugin = Path(PLUGINS_PATH) / plugin
        path_user_plugin = userPluginsDir / plugin
        ref_plugin_md = plugin_metadata_as_dict(path_ref_plugin)
        user_plugin_md = plugin_metadata_as_dict(path_user_plugin)

        isNewPlugin = True
        doNothing = False

        if plugin in userPlugins:
            compare = compareVersions(
                ref_plugin_md.get("general").get("version"), user_plugin_md.get("general").get("version")
            )
            if compare == 1:
                shutil.rmtree(path_user_plugin, ignore_errors=True)
                isNewPlugin = False
            else:
                doNothing = True

        if doNothing:
            continue

        copyPlugin(path_ref_plugin, path_user_plugin)

        settings = QgsSettings()
        if isNewPlugin:
            if startPlugin(plugin):
                settings.setValue("/PythonPlugins/" + plugin, True)
        else:
            if settings.value("/PythonPlugins/" + plugin, False, type=bool):
                reloadPlugin(plugin)
            else:
                unloadPlugin(plugin)
                loadPlugin(plugin)


def main():
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
    main()
