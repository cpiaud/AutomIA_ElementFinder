import json

from robot.api.deco import keyword


class AutomIAlib:

    @staticmethod
    def read_json_file(file_path:str) -> any:
        """
        Reads the content of a JSON file and returns it as a dictionary.

        Arguments:
        - file_path: Path to the JSON file to be read.

        Returns:
        - A dictionary containing the JSON data.
        """
        with open(file_path, 'r', encoding="utf8") as file:
            json_data:any = json.load(file)
        return json_data

    @staticmethod
    def read_properties_file(file_path:str) -> list[str]:
        with open(file_path, 'r') as file:
            # Read lines from the file
            lines = file.readlines()

        # Initialize an empty list to store properties and their values
        properties = []

        # Iterate over lines in the file
        for line in lines:
            # Split each line into property and value
            prop, value = line.strip().split('=')
            # Convert value to integer
            value = int(value)
            # Append property and value as tuple to the list
            properties.append((prop, value))

        # Sort the properties list based on the value (second element in the tuple)
        properties.sort(key=lambda x: x[1], reverse=True)

        # print(f"Properties file values:\n")
        # for propertyValue, value in properties:
        #     print(f"{propertyValue} = {value}")

        # Return sorted properties
        return properties
