import json

from robot.api.deco import keyword


class MyLibraryTest:

    @keyword
    def read_json_file_test(self, file_path):
        """
        Reads the content of a JSON file and returns it as a dictionary.

        Arguments:
        - file_path: Path to the JSON file to be read.

        Returns:
        - A dictionary containing the JSON data.
        """
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data
