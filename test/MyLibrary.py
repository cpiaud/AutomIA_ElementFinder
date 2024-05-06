import json
from robot.api.deco import keyword


class MyLibrary:

    @keyword
    def join_two_strings(self, arg1, arg2):
        return str(arg1) + " " + str(arg2)

    @staticmethod
    def generate_locators(json_data):
        locators = []

        # Extract information from JSON data
        tag_name = json_data.get('tagName')
        id_ = json_data.get('id')
        class_ = json_data.get('class')
        text_content = json_data.get('textContent')

        # Generate locators based on extracted information
        if id_:
            locators.append(f"id:{id_}")

        if class_:
            classes = class_.split()
            for class_name in classes:
                locators.append(f"class:{class_name}")

        if tag_name:
            locators.append(f"tag:{tag_name}")

        if text_content:
            locators.append(f"text:{text_content}")

        # Extract possible locators from parent elements
        parents = json_data.get('parents', [])
        parent_locators = []
        for parent in parents:
            parent_locators.extend(MyLibrary.generate_locators(parent))

        # Add parent locators as a separate dictionary key within locators
        locators.append({'parent_locators': parent_locators})

        for locator in locators:
            print("Generated Locators:", locator)

        return locators

    @keyword
    def process_json_file_and_generate_locators(self, file_path):
        json_data = self.read_json_file(file_path)
        locators = self.generate_locators(json_data)
        return locators

    @staticmethod
    def read_json_file(file_path):
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

    @staticmethod
    def read_properties_file(file_path):
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

        print(f"Properties file values:\n")
        for propertyValue, value in properties:
            print(f"{propertyValue} = {value}")

        # Return sorted properties
        return properties
