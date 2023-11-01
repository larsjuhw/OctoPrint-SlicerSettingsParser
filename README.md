# OctoPrint-SlicerSettingsParser

**NOTE: Only supports Slic3r, Simplify3D, and Cura currently; suggest more in issues; contributions welcome!**

Analyses gcode for slicer settings comments and adds additional metadata of such settings. Useless without plugin(s) to use the metadata. 

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/larsjuhw/OctoPrint-SlicerSettingsParser/archive/master.zip

<!-- You will most likely want to install another plugin to use the metadata. Such plugins of mine are:
 - [OctoPrint-SlicerSettingsTab](https://github.com/tjjfvi/OctoPrint-SlicerSettingsTab) -->
 

## Configuration

### Cura

Cura doesn't natively support injecting the slicer settings into the gcode, so you must add [this](https://gist.github.com/larsjuhw/3db286b71d9c91ca7c72d3fd3325af9f) to your start/end gcode. Preferably add it to the start gcode, so that you can configure this plugin to stop parsing when it sees the first extrusion command.

### Python regexes
**Cura**

If you use the start/end gcode provided above, use this regex:
```
^; (?P<key>\w+[\w\s]*) = (?P<val>.*)
```

**Slic3r**

```
^; (?P<key>[^,]*?) = (?P<val>.*)
```

**Simplify3D**

```
^;   (?P<key>.*?),(?P<val>.*)
```

**Other**

This plugin uses python regexes to parse the gcode.
Syntax can be easily found on the web.
There should be two named capturing groups, `key` and `val`.
Multiple regexes should be listed on seperate lines, ordered by precedence.
Any chars are allowed in the groups; `\n` will be replaced by newlines.

If you can not figure it out yourself, open an issue and I can take a look.
