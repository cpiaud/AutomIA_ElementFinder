from collections import Counter
import time
from bs4 import BeautifulSoup
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from AutomIAlib import AutomIAlib

class FindWebElements:
    
    # Path to the attributes weight definition file
    attributes_weight_file_path = "resources/attributesWeight.properties"

    def __init__(self) -> None:
        self.AutomIAlib = AutomIAlib()

    def filter_elements_by_tag_name_by_driver(self, tag_name:str) -> any:
        """
        Filter elements by tag name using Selenium WebDriver.

        Args:
            tag_name (str): tag name of the scanned element JSON file.

        Returns:
            list: A list of DOM elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        # Get DOM elements by tag name
        script = f"return document.getElementsByTagName('{tag_name}')"
        dom_elements = selenium_lib.driver.execute_script(script)

        return dom_elements

    def get_element_attributes(self, scanned_element_json:any) -> list[any]:
        """
        Get all the attributes and their weight of the scanned_element_json.
        if one of the found attribute has no weight define in the attributes_weight file, is default weight will be 10

        Args:
            scanned_element_json (json): scanned element JSON data.
        
        Returns:
            list[(key, value, weight)]: A list of tuples containing this attribute key is value and is weight.
        """
        # Read the attribute weight properties file
        file_attributes = self.AutomIAlib.read_properties_file(self.attributes_weight_file_path)
        # Extract values based on the sorted attribute list
        attributes = []

        for attr in scanned_element_json:
            in_attributes_weight_file = False

            if attr in ['parents', 'siblings']: # special case
                continue
            for key, weight in file_attributes:
                if attr == key:
                    in_attributes_weight_file = True
                    attributes.append((attr, scanned_element_json[attr], weight))
                    break
            if not in_attributes_weight_file:
                attributes.append((attr, scanned_element_json[attr], 10))

        return sorted(attributes, key=lambda elm: elm[2], reverse=True) # sort the attributes by decreasing weight order

    def get_by_attributes(self, scanned_element_json:any) -> list[any]:
        """
        Get all corresponding elements with the attributes of the scanned element.

        Args:
            scanned_element_json (json): scanned element JSON data.

        Returns:
            list: A list of filtered elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        # Get the tagName of the element to retrieve in the DOM
        tag_name = scanned_element_json.get("tagName")
        # Get all the DOM elements possible for the element to find
        starting_list = self.filter_elements_by_tag_name_by_driver(tag_name)
        # Get all the attribute and their value to begin the search
        sorted_tag_list = self.get_element_attributes(scanned_element_json)
        # The most accurate list of possible element found by the attributes search
        current_cached_list = starting_list
        # The list of possible elements found by the current attribute
        filtered_elements = []

        for attribute_name, value, _ in sorted_tag_list:
            if attribute_name == "textContent":
                xpath = f"//{tag_name}[contains(., '{value}')]"
            else:
                xpath = f"//{tag_name}[@{attribute_name}='{value}']"

            filtered_elements = selenium_lib.driver.find_elements(By.XPATH, xpath)

            if len(filtered_elements) == 1: # Element found
                current_cached_list = filtered_elements
                break
            elif len(filtered_elements) > 1: # Multiple elements found
                if len(filtered_elements) < len(current_cached_list):
                    current_cached_list = filtered_elements
                else:
                    filtered_elements = current_cached_list

        return current_cached_list

    def check_by_siblings(self, siblings, soup) -> list[any]:
        """
        This method check if one of the siblings is present and try to recongised the researched element
        by creating a list of all of the siblings in the soup element and compared them with the siblings of the research element

        Args:
            siblings (list[json]): the list of all of the siblings element of the reasearched element
            soup (Beautifullsoup): the html node where we gonna try to find the researched element
        Returns:
            list : the list of plausible research element in format Beautifullsoup
        """
        is_one_child_found = False
        childrens = []
        res = []

        for sc in soup.children:
            if sc != "\n":
                childrens.append(sc)
                res.append(sc)

        for c in childrens:
            for s in siblings:
                same_element = True
                for attr in s.keys():
                    match attr:
                        case 'tagName':
                            same_element = c.name.__eq__(s[attr])
                        case 'textContent':
                            same_element = c.get_text().strip().__eq__(s[attr])
                        case _:
                            same_element = c[attr][0].strip().__eq__(s[attr])
                    if not same_element:
                        break
                if same_element:
                    is_one_child_found = True
                    res.remove(c)
                    continue
        return res if is_one_child_found else []

    def get_to_parent(self, parents, siblings, soup) -> list[any]:
        """
        Recursive method to reach the last known parent of the researching element before comparing the found elements and the siblings elements

        Args:
            parents (list[json]): the list of all of the parent element of the researched element
            siblings (list[json]): the list of all of the siblings element of the reasearched element
            soup (Beautifullsoup): the html node where we gonna try to find the researched element
        Returns:
            list : the list of plausible research element in format Beautifullsoup
        """
        find_elements = []

        if not parents:
            e = self.check_by_siblings(siblings, soup)
            for el in e:
                find_elements.append(el)
        else:
            for elm in soup.find_all(parents[len(parents) - 1]["tagName"]):
                if (len(parents) - 1 >= 0):
                    e = self.get_to_parent(parents[:-1], siblings, elm)
                    if e:
                        find_elements.extend(e)

        return find_elements if find_elements else None

    def create_xpath_for_soup_element(self, soupElm:str) -> str:
        """
        Create the xpath of a BeautifullSoup element

        Args:
            soupElm (str): The BeautifullSoup element

        Returns:
            str: the xpath of the element.
        """
        xpath = f"//{soupElm.name}["
        is_starting_attribute = True

        for attr in soupElm.attrs:
            match attr:
                case 'name':
                    continue
                case 'class':
                    res = ""
                    for c in soupElm["class"]:
                        res += ' ' + c
                    res = res.strip()
                    xpath += f" and @{attr}='{res}'" if not is_starting_attribute else f"@{attr}='{res}'"
                case 'textContent':
                    xpath += f" and contains(., '{soupElm[attr]}')" if not is_starting_attribute else f"contains(., '{soupElm[attr]}')"
                case _:
                    xpath += f" and @{attr}='{soupElm[attr]}'" if not is_starting_attribute else f"@{attr}='{soupElm[attr]}'"
            is_starting_attribute = False
        return xpath + "]"

    def get_by_siblings_and_parents(self, scanned_element_json:any) -> any:
        """
        Get all corresponding elements with the parents and siblings of the scanned element.

        Args:
            scanned_element_json (json): scanned element JSON data.

        Returns:
            list: A list of the plausible corresponding elements.
        """
        # Initialize a SeleniumLibrary instance
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        soup = BeautifulSoup(selenium_lib.driver.page_source, 'html.parser')

        soupElms = self.get_to_parent(scanned_element_json["parents"][:-1], scanned_element_json["siblings"], soup)
        if len(soupElms) != 1:
            return []
        
        web_elm_xpath = self.create_xpath_for_soup_element(soupElms[0])
        return selenium_lib.driver.find_elements(By.XPATH, web_elm_xpath)


    def match_count(self, element_siblings, siblings_properties):
        """
        Compte le nombre de correspondances entre les propriétés des siblings d'un élément
        et la liste des propriétés spécifiées dans siblings_properties.

        Arguments:
        - element_siblings: Liste de WebElement représentant les siblings d'un élément.
        - siblings_properties: Liste de dictionnaires contenant les propriétés à matcher.

        Retourne:
        - Nombre d'éléments correspondants dans element_siblings.
        """
        count = 0
        for sibling, prop in zip(element_siblings, siblings_properties):
            # Vérifie les correspondances des propriétés
            if (
                sibling.tag_name == prop["tagName"] and
                sibling.text.strip() == prop["textContent"]
            ):
                count += 1
        return count

    
    def find_best_element_with_siblings(self, attributes_way_result, siblings):
        """
        Trouve l'élément de attributes_way_result ayant le plus de siblings correspondant
        aux propriétés spécifiées dans la liste siblings.

        Arguments:
        - attributes_way_result: Liste d'éléments WebElement trouvés par Selenium.
        - siblings: Liste de dictionnaires représentant les propriétés des siblings d'un élément.

        Retourne:
        - L'élément WebElement de attributes_way_result ayant le plus de correspondances avec siblings.
        """

        # Initialisation des variables pour suivre le meilleur élément
        best_element = None
        max_matches = 0
        elem = 0

        # Parcours de chaque élément pour trouver celui avec le maximum de correspondances
        for element in attributes_way_result:
            # Obtenez tous les siblings de l'élément
            element_siblings = element.find_elements(By.XPATH, "following-sibling::*")
            
            # Appel de match_count pour calculer le nombre de correspondances avec siblings
            matches = self.match_count(element_siblings, siblings)
            elem = elem + 1
            print(f"Elements {elem} a {matches} frères en commun avec l'élément cherché")

            # Met à jour le meilleur élément si un nombre plus élevé de correspondances est trouvé
            if matches > max_matches:
                max_matches = matches
                best_element = element

        return best_element


    # Fonction pour faire clignoter l'élément
    def blink_element(self, element, duration=3, interval=0.3):
        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        # Faire défiler pour amener l'élément dans la vue
        selenium_lib.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)  # Pause pour s'assurer que le défilement est terminé

        end_time = time.time() + duration
        while time.time() < end_time:
            # Changer la couleur de fond en jaune
            selenium_lib.driver.execute_script("arguments[0].style.backgroundColor = 'blue'", element)
            time.sleep(interval)
            
            # Remettre la couleur de fond d'origine
            selenium_lib.driver.execute_script("arguments[0].style.backgroundColor = ''", element)
            time.sleep(interval)


    def find_most_frequent_element_by_siblings(self, json_sibling_properties):
        """
        Trouve l'élément web ayant le plus de correspondances de siblings selon les propriétés du JSON.
        
        Arguments:
        - driver: Instance de WebDriver de Selenium.
        - json_sibling_properties: Liste de dictionnaires contenant les propriétés des siblings.

        Retourne:
        - L'élément WebElement apparaissant le plus souvent dans les listes fusionnées.
        """

        selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        # Initialiser la liste fusionnée pour tous les éléments trouvés
        all_elements = []

        # Parcourir chaque groupe de propriétés de sibling dans le JSON
        for sibling_props in json_sibling_properties:
            # Construire un XPath basé sur les propriétés pour identifier les siblings
            xpath = f"{sibling_props['tagName']}[contains(., '{sibling_props['textContent']}')]"
            # Rechercher les éléments ayant des siblings correspondant à ce XPath
            matching_elements = selenium_lib.driver.find_elements(By.XPATH, f"//*[following-sibling::{xpath} or preceding-sibling::{xpath}]")
            # Ajouter les éléments trouvés à la liste fusionnée
            all_elements.extend(matching_elements)

        # Utiliser Counter pour compter les occurrences de chaque élément
        element_counts = Counter(all_elements)

        # Trouver l'élément apparaissant le plus souvent dans la liste fusionnée
        most_frequent_element = element_counts.most_common(1)[0][0] if element_counts else None
        self.blink_element(most_frequent_element)

        return most_frequent_element


    def find_elements_by_ia_with_driver(self, scanned_element_json_name:str) -> any:
        """
        Find elements by IA using Selenium WebDriver.

        Args:
            scanned_element_json_name (str): Name of the scanned element JSON file.

        Returns:
            list: A list of unique elements found.
        """
        # Get the data of the element json file
        scanned_element_json = self.AutomIAlib.read_json_file(f'{scanned_element_json_name}.json')
        attributes_way_result = self.get_by_attributes(scanned_element_json)
        
        # TODO reinforce the error handling
        if (len(attributes_way_result) > 1):
            print(f"nombre d'élements encore en lice : {len(attributes_way_result)}")
#            return self.get_by_siblings_and_parents(scanned_element_json)
#            print(f"Elements toujours en lice : {attributes_way_result}")
#            print(f"propriétés des frères de l'élément cherché : {scanned_element_json["siblings"]}")
 #           return self.find_best_element_with_siblings(attributes_way_result, scanned_element_json["siblings"])
            return self.find_most_frequent_element_by_siblings(scanned_element_json["siblings"])

        return attributes_way_result
