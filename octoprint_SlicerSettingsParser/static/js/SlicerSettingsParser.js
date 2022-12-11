$(() => {
	function SlicerSettingsParserViewModel([ settingsViewModel ]){
		let self = this;

		self.settingsViewModel = settingsViewModel;

		self.analyzing_files = ko.observable(false);
		self.done_analysis = ko.observable(false);
		
		self.analyzeAll = () => {
			console.log("SlicerSettingsParser analyze_all");
			self.analyzing_files(true);
			self.done_analysis(false);
			// $('#analyze_files_info').css('display', '');
			$.ajax({
			    url: API_BASEURL + "plugin/SlicerSettingsParser",
			    type: "POST",
				data:  JSON.stringify({ command: "analyze_all" }),
				contentType: "application/json; charset=UTF-8",
			})
			.then((data) => {
				self.analyzing_files(false);
				self.done_analysis(true);
			});
		};
		
		self.onBeforeBinding = () => {
			self.settings = settingsViewModel.settings.plugins.SlicerSettingsParser;
			self.joinedRegexes = ko.computed({
				read: () => self.settings.regexes().join("\n"),
				write: rs => self.settings.regexes(rs.split("\n")),
			});
		};
	}

    OCTOPRINT_VIEWMODELS.push({
        construct: SlicerSettingsParserViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_SlicerSettingsParser"],
    });
})
