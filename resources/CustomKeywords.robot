*** Settings ***
Library    AutomIAlib.py
Library    FindWebElements.py
Library    SeleniumLibrary
Library    String
Library    Collections
Variables   ./settings.yaml

*** Keywords ***
AutomIA Locator Strategy
    [Arguments]    ${browser}    ${locator}   ${tag}    ${constraints}
    ${locator_parts}=    Split String    ${locator}    |
    ${nbProperties}=    Get length    ${locator_parts}
    ${objFile}=    Set Variable    ${locator_parts[0]}
    ${objPath}=    Set Variable    ${EXECDIR}${ObjectRepositoryPath}
    ${additionalProperties}=    Create Dictionary
    # transform the additional properties passed as parameters to dictionary
    FOR    ${index}    IN RANGE    1    ${nbProperties}
        ${property}=    Split String    ${locator_parts[${index}]}    :
        ${propertyName}=    Set Variable    ${property[0]}
        ${propertyValue}=    Set Variable    ${property[1]}
        Set To Dictionary    ${additionalProperties}    ${propertyName}    ${propertyValue}
    END    
 #  Log To Console     nbCustomProperties : ${nbProperties}
 #  Log To Console     Object Path : ${objPath}
    ${webelement}=     Find Elements By IA With Driver   ${objPath}    ${objFile}    ${additionalProperties}
    RETURN    ${webelement}

Attendre Que Le Texte Soit Stable
    [Documentation]    Waits until the visible text on the page no longer changes between two 0.1s intervals, with a maximum of 30 attempts.
    ${attempts_max}=    Set Variable    30
    ${intervalle}=        Set Variable    0.1s

    FOR    ${i}    IN RANGE    ${attempts_max}
        ${texte1}=    Get Text    xpath=//body
        Sleep    ${intervalle}
        ${texte2}=    Get Text    xpath=//body
        ${result}=    Run Keyword And Ignore Error    Should Be Equal    ${texte1}    ${texte2}
        Run Keyword If    '${result}[0]' == 'PASS'    Exit For Loop
        Log To Console    Unstable text on attempt ${i + 1}
    END

Attendre Que Le DOM Soit Stable
    [Documentation]    Waits until the total number of elements in the DOM no longer changes
    ...                between two intervals, indicating structural stability.
    [Arguments]    ${attempts_max}=10    ${intervalle}=0.2s    ${locator_racine}=xpath=//*
    # Arguments optionnels: attempts_max, intervalle, locator_racine (pour cibler une partie du DOM si besoin)

    # GCL MODE SILENCIEUX
    # Log To Console    INFO: Attente de la stabilisation du DOM (max ${tentatives_max} tentatives, intervalle ${intervalle})...
    FOR    ${i}    IN RANGE    ${attempts_max}
        ${compte1}=    Get Element Count    ${locator_racine}
        Sleep    ${intervalle}
        ${compte2}=    Get Element Count    ${locator_racine}

        # Comparaison directe des nombres
        IF    ${compte1} == ${compte2}
            # GCL MODE SILENCIEUX
            # Log To Console    INFO: Le nombre d'éléments (${compte1}) est stable. DOM considéré comme stable.
            RETURN      # Sortir du keyword dès que c'est stable
        # ELSE
            # GCL MODE SILENCIEUX
            # Log To Console    DEBUG: Nombre d'éléments instable à la tentative ${i + 1} (${compte1} vs ${compte2}). Attente de ${intervalle}...
        END
    END
    # Si la boucle se termine sans stabilisation
    Fail    ERREUR: Le nombre d'éléments dans le DOM ne s'est pas stabilisé après ${attempts_max} tentatives.

Page Should Have Ready State Complete
    ${state}=    Execute Javascript    return document.readyState;
    Should Be Equal    ${state}    complete    L'état de la page n'est pas 'complete' (actuel: ${state}).

 
Strong
    [Arguments]    ${mot_cle}    @{args}
    [Documentation]    Exécute un mot-clé avec rerejeu automatique en cas d'exception dans la limite d'un nombre de fois en paramètre ci-dessous. 
    ...                Utile pour gérer les erreurs comme StaleElementReferenceException ou autres erreurs intermittentes.
    ${tentatives_max}=    Set Variable    10
    ${attente}=           Set Variable    0.1s

    # Page Should Have Ready State Complete
    # Attendre Que Le Texte Soit Stable      # Moins robuste qu'attendre que le DOM soit Stable.
    Attendre Que Le DOM Soit Stable
    # Wait Until Keyword Succeeds    10x    0.1s    Page Should Have Ready State Complete
    FOR    ${index}    IN RANGE    ${tentatives_max}
        TRY
            ${result}=    Run Keyword    ${mot_cle}    @{args}
            Log    ✅ Succès à la tentative ${index + 1} pour : ${mot_cle} ${args}
            RETURN    ${result}
        EXCEPT    AS    ${err} 
            Log To Console    ❌ Échec tentative ${index + 1} pour : ${mot_cle} ${args}
            Log To Console    Message d'exception : ${err}
            Sleep    ${attente}
        END
    END
    Fail    ❌ Échec après ${tentatives_max} tentatives du mot-clé : ${mot_cle} ${args}. Dernière erreur: ${err}
