# AutomIA_ElementFinder
Recherche d'élements Web via robot framework à partir d'une description JSON de l'élément à trouver


# Guide étape par étape:

1. Importez la librairie BeautifulSoup.

```sh
pip install beautifulsoup4
```

2. Importez la bibliothèque FindElementByIA dans votre test.

```robot
Library     FindElementByIA.py
```
3. Utilisez la stratégie de localisation personnalisée de Robot Framework dans la section keyword pour pouvoir définir les localisateurs personnalisés.

```robot
*** Keywords ***

Custom Locator Strategy for IA
[Arguments]    ${browser}    ${locator}    ${tag}    ${constraints}
${webelement}=     Find Elements By IA With Driver   ${locator}
[Return]    ${webelement}
```

4. Utilisez les localisateurs personnalisés dans vos tests comme l'exemple suivant :

```robot
*** Test Cases ***

Find Web Elements By IA Test
Add Location Strategy    FindElementsByIA    Custom Locator Strategy for IA
Open Browser        ${loginpageurl}     chrome
Input Text      FindElementsByIA:login_username  ${username}
```
Custom Locator Strategy for IA est le nom de notre Location Strategy
FindElementsByIA est le nom de notre Custom locator
login_username est le nom de notre fichier json
