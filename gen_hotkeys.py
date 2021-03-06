"""
Auto-SC2-Hotkeys-File

Author:
    Christian P. Byrne

Since:
    Sep 21

Requirements:
    json

Link:
    https://github.com/trevor-reznik/SC2-hotkeys-file-generator

Filename:
    grid.py

Grid Layout:

    Indices:
        1   2  3  4  5

        6   7  8  9  10

        11  12 13 14 15

    Default Keys:
        q w e r t

        a s d f g

        z x c v b


"""

import os
import json
from tests import test_cases


def pwd():
    """Return string of absolute path of script directory."""
    return os.path.dirname(os.path.realpath(__file__))


def find_file(keywords, sub_dir=""):
    """Find first file in script's directory that includes all keywords.

    Args:
        keywords (list) : File must include each str element to be a match.
        sub_dir (str)   : Indicate path string relative to script root, 
        enclose with a /.

    Returns:
        str : Absoute path of first match.


    """
    dir_path = pwd()
    for fi in os.listdir(f"{dir_path}/{sub_dir}"):
        for keyword in keywords:
            # Must include all keywords.
            if keyword not in fi:
                continue

            # Return first match only.
            return f"{dir_path}/{sub_dir}{fi}"


class WhichRace:
    def __init__(self, verbose=False):
        self.protoss, self.zerg, self.terran = \
            self._read_units_txt().values()
        self.verbose = verbose

    def which(self, hotkey):
        """Mostly accurate method to determine race that a hotkey assignment belongs to.

        Args:
            hotkey (str) : How the hotkey assignment appears in the .SC2Hotkeys file, 
                without the newline character. Casing doesn't matter.

        Returns:
            (str): all, terran, protoss, or zerg.


        """
        units = "".join(hotkey.lower().split("=")[:-1])
        units = units.split("/")
        cur = False
        for l in units:
            for race, name in zip([self.protoss, self.terran, self.zerg], ["protoss", "terran", "zerg"]):
                if name in l:
                    return name
                for race_unit in race:
                    if race_unit in l:
                        # If multiple matches, might be shared keyword like "Build" or "Upgrade"
                        # In which case, return 'all' to be safe.
                        if cur and cur != name:
                            print(f"multi-match")
                            return "all"
                        # Set cur to race name if it is first match.
                        cur = name

        # Verbose mode for debugging or seeing process.
        if self.verbose:
            print(
                hotkey,
                f"{cur if cur else 'all'}",
                "",
                sep="\n"
            )

        return "all" if not cur else cur

    def _read_units_txt(self):
        """Read and parse the list of units/buildings by race.
        """
        ret = {"protoss": [], "zerg": [], "terran": []}

        for race in ret.keys():
            txt_file = find_file([race], "data/units-buildings/")
            lines = open(txt_file, "r").readlines()
            for line in lines:
                cleaned = ""
                # Filter out non-alpha characters.
                for char in line:
                    if char.isalpha():
                        cleaned += char

                # Don't add empty lines.
                if cleaned:
                    ret[race].append(cleaned.lower())

        return ret


class GridHotkeys:
    def __init__(self, race, profile_name, custom_grid=False, grid_key_prefix="", verbose=False):
        """
        Implements:
            WhichRace

        Args:
            race (str) : protoss, terran, zerg, or all.


        """
        self.race = race
        self.raw = self._read_json()
        self.find_race = WhichRace(verbose=verbose)
        self.race_hotkeys = self._filter_race()

        self.reference_grid = [
            "q", "w", "e", "r", "t",
            "a", "s", "d", "f", "g",
            "y", "x", "c", "v", "b"
        ]
        self.default_grid = [
            "q", "w", "e", "r", "t",
            "a", "s", "d", "f", "g",
            "z", "x", "c", "v", "b"
        ]
        self.grid_key = custom_grid or self.default_grid
        self.prefix = grid_key_prefix
        self.profile_name = profile_name

    def _hotkeys_output(self):
        """Return text meant for hotkey file output."""
        ret_keys = []

        for hotkey in self.race_hotkeys:
            curr_key = hotkey.split("=")[-1]
            unit = hotkey.split("=")[:-1]

            # Only rebind hotkeys that are alrady a part of grid
            # I.e., don't try to reassign hotkeys outside of grid
            # like control groups, camera control, etc.
            if curr_key.lower() in self.reference_grid:
                new_key = self.grid_key[self.reference_grid.index(curr_key.lower())]
                new_key = self.prefix + new_key.upper()
                ret_keys.append(
                    f"{''.join(unit)}={new_key}"
                )

        return ret_keys

    def gen_hotkey_file(self):
        """Write the results of the script to a new .SC2Hotkeys file in the 
        current directory. 

        There is some syntax present in all these files which 
        I include but I am not sure if it is even necessary. The 'CamerCenter' 
        hotkey is disabled because it was causing problems for unknown reasons.


        """
        output_file = open(f"{pwd()}/{self.profile_name}.SC2Hotkeys", "w")
        output_file.write(
            "[Settings]\n\n[Hotkeys]\nCameraCenter=\n\n[Commands]\n")
        for hotkey in self._hotkeys_output():
            output_file.write(hotkey + '\n')
        output_file.close()

    def _read_json(self):
        """Read json file which contains raw hotkey assignments

        Returns:
            dict: 
                { "raw" : ["ability/unit=hotkey"...] }


        """
        with open(find_file(["raw", "json"], sub_dir="data/"), "r") as json_file:
            data = json.load(json_file)
            return data["raw"]

    def _filter_race(self):
        """Filter all hotkey assignments by race of class instance or hotkeys
        that apply to all races.
        """
        ret = []
        for hotkey in self.raw:
            hotkeys_race = self.find_race.which(hotkey)
            if hotkeys_race == "all" or hotkeys_race == self.race.lower():
                ret.append(hotkey)

        return ret


def get_user_grid():
    """Read and return a custom grid if user opts in."""
    if "y" in input("Do you want to use a custom grid? [Y/N]\n"):
        print(
            "Type the first line of the grid as lowercase letters separated by spaces (e.g., 'q w e r'")
        first = input()
        second = input("Type second line:\n")
        third = input("Type third line:\n")

        return first.split(" ") + second.split(" ") + third.split(" ")
    return False


def main():
    race = input("What race do you play?\n").lower()
    grid = get_user_grid()
    prefix = ""
    if "y" in input("Prefix grid hotkeys with another key (e.g., Shift or Ctrl)? [Y/N]\n").lower():
        prefix = input(
            "Type prefix (format like 'Shift', 'Alt', 'Control'):\n") + "+"
    name = input(
        "What should the name of the hotkey profile be? (no space):\n")

    hotkey_profile = GridHotkeys(
        race, name, custom_grid=grid, grid_key_prefix=prefix)
    hotkey_profile.gen_hotkey_file()


if __name__ == "__main__":
    main()
