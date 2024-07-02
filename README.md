**# AutomIA_ElementFinder**

Recherche d'éléments Web via la librairie Selenium de Robot Framework à partir d'un fichier JSON contenant toutes les propriétés de l'élément à trouver

**# Guide étape par étape:**

1. Importez la librairie BeautifulSoup.

```sh

pip install beautifulsoup4

```

2. Mettez à jour la variable ${ObjectRepositoryPath}  dans le fichier resources/CustomKeywords.robot avec le chemin de votre objectrepository

```robot
*** Settings ***
Library AutomIAlib.py
Library FindWebElements.py
Library SeleniumLibrary

*** Variables ***
${ObjectRepositoryPath}  /demo/objectrepository/

*** Keywords ***
AutomIA Locator Strategy
[Arguments] ${browser} ${locator} ${tag} ${constraints}
${objPath} =  Set Variable  ${EXECDIR}${ObjectRepositoryPath}${locator}
${webelement}= Find Elements By IA With Driver ${objPath}
RETURN ${webelement}
```

Votre objectrepository contiendra tous les fichiers json des éléments que vous voulez utiliser dans vos tests.

Pour alimentez ce dossier vous pouvez utiliser la méthode présenter dans ce repo github [https://github.com/cpiaud/AutomIA_SpyWeb.](https://github.com/cpiaud/AutomIA_SpyWeb. "https://github.com/cpiaud/automia_spyweb.")

3. Dans vos fichier de tests il ne vous reste plus qu'à importer votre fichier contenant le keyword de localisation personnalisé.

```robot
*** Settings ***
Resource ./pathToYour/CustomKeywords.robot
Library SeleniumLibrary
```

Prenez soin de bien vérifier le chemin de votre fichier contenant votre Location Strategy

4. Ajouter la nouvelle stratégie de localisation "Add Loacation Strategy" et utilisez ensuite les localisateurs personnalisés dans vos tests comme l'exemple suivant :

```robot
*** Test Cases ***
Test Name
Add Location Strategy FindElementsByIA AutomIA Locator Strategy
Open Browser ${loginpageurl} chrome
Input Text FindElementsByIA:login_username ${username}
```

"AutomIA Locator Strategy" est le nom de notre Location Strategy
"FindElementsByIA" est le nom de notre Custom locator
"login_username" est le nom de notre fichier json