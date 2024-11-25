# coding=utf-8
import re
from os import path as ospath

import octoprint.filemanager
import octoprint.plugin
import octoprint.util.comm
from file_read_backwards import FileReadBackwards
from octoprint.events import Events


class SlicerSettingsParserPlugin(
	octoprint.plugin.StartupPlugin,
	octoprint.plugin.EventHandlerPlugin,
	octoprint.plugin.SettingsPlugin,
	octoprint.plugin.TemplatePlugin,
	octoprint.plugin.AssetPlugin,
	octoprint.plugin.SimpleApiPlugin,
):
	def on_after_startup(self):
		self._storage_interface = self._file_manager._storage("local")
		self._logger.info("SlicerSettingsParser still active")

	def get_settings_defaults(self):
		return dict(
			regexes=[
				"^; (?P<key>[^,]*?) = (?P<val>.*)",
				"^;   (?P<key>.*?),(?P<val>.*)",
			],
			limit="none",
			maxlines=100,
			search_backwards=False
		)

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=True)
		]

	def get_assets(self):
		return dict(js=["js/SlicerSettingsParser.js"])
	
	def register_custom_events_hook(*args, **kwargs):
		return ['file_analyzed']
	
	def send_file_analyzed_event(self, path: str):
		event = Events.PLUGIN_SLICER_SETTINGS_PARSER_FILE_ANALYZED
		payload = {
			'path': path
		}
		self._event_bus.fire(event, payload=payload)

	def get_api_commands(self):
		return dict(
			analyze_all=[]
		)

	def on_api_command(self, command, data):
		self._logger.info(f"Received api command: {command}")
		if command == "analyze_all":
			self._analyze_all()

	def on_event(self, event, payload):
		if event != "FileAdded" or payload["storage"] != "local" or ospath.splitext(payload["name"])[-1].lower() not in [".gcode",".gco",".g"]:
			return

		self._analyze_file(payload["path"])

	def _analyze_all(self):
		def recurse(files):
			for item in files.values():

				if item["type"] == "folder":
					recurse(item["children"])
					continue

				if item["typePath"][-1] != "gcode":
					continue

				self._analyze_file(item["path"])

		recurse(self._storage_interface.list_files())

	def _analyze_file(self, path):
		self._logger.info(f"Analyzing file: {path}")

		slicer_settings = dict()
		regexes = [re.compile(x) for x in self._settings.get(["regexes"])]

		limit = self._settings.get(['limit'])
		max_lines = int(self._settings.get(['maxlines']))

		search_backwards = self._settings.get(["search_backwards"])
		method = FileReadBackwards if search_backwards else open

		with method(self._storage_interface.path_on_disk(path)) as file:
			for i, line in enumerate(file):
				if limit == 'lines' and i > max_lines:
					break
				if limit == 'extrusion' and octoprint.util.comm.gcode_command_for_cmd(line) == 'G1':
					break
				for regex in regexes:
					match = regex.search(line)
					if not match:
						continue

					key, val = match.group("key", "val")
					slicer_settings[key] = val
					break

		self._storage_interface.set_additional_metadata(path, "slicer_settings", slicer_settings, overwrite=True)
		self.send_file_analyzed_event(path)
		self._logger.info(f"Saved slicer settings metadata for file: {path}")

	def get_update_information(self):
		return {
			"SlicerSettingsParser": {
				"displayName": "SlicerSettingsParser Plugin",
				"displayVersion": self._plugin_version,

				# version check: github repository
				"type": "github_release",
				"user": "larsjuhw",
				"repo": "OctoPrint-SlicerSettingsParser",
				"current": self._plugin_version,
                "stable_branch": {
                    "name": "Stable",
                    "branch": "master",
                    "comittish": ["master"],
                }, "prerelease_branches": [
                    {
                        "name": "Release Candidate",
                        "branch": "rc",
                        "comittish": ["rc", "master"],
                    }
                ],
				# update method: pip
				"pip": "https://github.com/larsjuhw/OctoPrint-SlicerSettingsParser/archive/{target_version}.zip"
			}
		}

__plugin_name__ = "SlicerSettingsParser"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = SlicerSettingsParserPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.events.register_custom_events": __plugin_implementation__.register_custom_events_hook,
	}
