*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${BROWSER}    Chrome
${URL}    file:///${CURDIR}/SiteRegEx/listePrix.html

*** Test Cases ***
Récupérer le montant des Fraises
    Open Browser    ${URL}    ${BROWSER}
    ${texte_fraises}    Get Text    xpath=//li[contains(text(), 'Fraise')]
    ${montant}    Run Keyword If    '${texte_fraises}' != ''    Evaluate    re.search(r'\d+[.,]?\d*', '''${texte_fraises}''').group() if re.search(r'\d+[.,]?\d*', '''${texte_fraises}''') else 'Montant non trouvé'    re
    Log    ${montant}
    Close Browser

Ajouter Banane Et Tomate Au Panier
    Open Browser    ${URL}    ${BROWSER}
    Click Element    xpath=//li[contains(text(), 'Banane')]
    Click Element    xpath=//li[contains(text(), 'Tomate')]
    ${panier}    Get Text    id=listePanier
    Should Contain    ${panier}    Banane - 1.80€/kg
    Should Contain    ${panier}    Tomate - 2.80€/kg
    Close Browser