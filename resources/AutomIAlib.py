from robot.api.deco import keyword
import json


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

    @staticmethod
    def update_json_file(file_path: str, key_value: str):
        """
        Updates a JSON file by adding or modifying a key-value pair at the root level.

        Arguments:
        - file_path: Path to the JSON file to be modified.
        - key_value: String representing the key-value pair in the format "key:value".
        """
        # Split the key_value string into key and value
        key, value = key_value.split(':', 1)
        # Convert value to int if it's numeric, otherwise keep it as a string
        value = int(value) if value.isdigit() else value

        # Load the existing JSON data
        file_path = file_path + ".json"
        with open(file_path, 'r', encoding="utf8") as file:
            json_data = json.load(file)

        # Update or add the key-value pair
        json_data[key] = value

        # Write the modified JSON data back to the file
        with open(file_path, 'w', encoding="utf8") as file:
            json.dump(json_data, file, ensure_ascii=False, indent=4)