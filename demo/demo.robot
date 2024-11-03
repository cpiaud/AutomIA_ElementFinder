*** Settings ***
Resource   ../resources/CustomKeywords.robot
Library    SeleniumLibrary


*** Variables ***
${BROWSER}    chrome
${siteDemo}    SiteDemoOriginal  # "SiteDemoOriginal" or "SiteDemoEvoTexte" or "SiteDemoEvoTech" or "SiteDemoRefonte"
${username}     myUsername
${password}     myPassword
${firstnamevalue}     myFirstname
${lastnamevalue}     myLastname
${emailvalue}     myemail@email.com
${addressvalue}     myAddress
${cityvalue}     Nantes
${zipcodevalue}     44000
${countryvalue}     FR
${appliedpositionvalue}     QA Lead
${coverlettervalue}     this is my test sentence
${yearsexperiencevalue}     8
${startdatevalue}   13/06/2024
${mobilenumbervalue}    06 77 77 77 77
${testlibrary}      MyText
${email_locator}    ${EMPTY}
${browser}    ${EMPTY}
${locator}    ${EMPTY}
${tag}    ${EMPTY}
${constraints}   ${EMPTY}


*** Keywords ***


*** Test Cases ***
TestClassicRobotFramework
    [Tags]  Classic
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/${siteDemo}/Login.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Log to Console  login
    Wait Until Element Is Visible   name:email
    Input Text   name:email   ${username}
    Input Text   name:pass   ${password}
    Click Element    xpath://a[text()='Connexion']
    Log to Console  job application form
    Wait Until Element Is Visible  id:fluentform_153
    Input Text	    id:ff_153_names_first_name_    ${firstnamevalue}
    Input Text      id:ff_153_names_last_name_     ${lastnamevalue}
    Input Text	    id:ff_153_email        ${emailvalue}
    Input Text  	id:ff_153_phone      ${mobilenumbervalue}
    Input Text  	id:ff_153_address_1_address_line_1_      ${addressvalue}
    Input Text      id:ff_153_address_1_city_     ${cityvalue}
    Input Text	    id:ff_153_address_1_zip_      ${zipcodevalue}
    Select From List by Value	    id:ff_153_address_1_country_      ${countryvalue}
    Input Text	    id:ff_153_input_text      ${appliedpositionvalue}
    Input Text	    id:ff_153_description_3      ${coverlettervalue}
    Input Text	    id:ff_153_numeric-field      ${yearsexperiencevalue}
    Click Element   xpath://a[text()='Apply']
    Wait Until Element Is Visible   xpath://main/div/div[2]/div/form
    Log to Console   Job application complete
    Close Browser

TestAvecAutomIA
    [Tags]  AutomIA
    Add Location Strategy    FindElementsByIA    AutomIA Locator Strategy   ${True}
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/${siteDemo}/Login.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Log to Console  login
    Wait Until Element Is Visible       FindElementsByIA:login_username|textContent:User Name|index:6
    Input Text      FindElementsByIA:login_username  ${username}
    Input Text      FindElementsByIA:login_password  ${password}
    Click Element   FindElementsByIA:login_ConnexionButton
    Log to Console  job application form
    Wait Until Element Is Visible       FindElementsByIA:JobApp_FirstName
    Input Text	    FindElementsByIA:JobApp_FirstName    ${firstnamevalue}
    Input Text      FindElementsByIA:JobApp_LastName     ${lastnamevalue}
    Input Text	    FindElementsByIA:JobApp_Email        ${emailvalue}
    Input Text  	FindElementsByIA:JobApp_MobileNumber      ${mobilenumbervalue}
    Input Text  	FindElementsByIA:JobApp_Address      ${addressvalue}
    Input Text      FindElementsByIA:JobApp_City     ${cityvalue}
    Input Text	    FindElementsByIA:JobApp_ZipCode      ${zipcodevalue}
    Select From List by Value	    FindElementsByIA:JobApp_Country      ${countryvalue}
    Input Text	    FindElementsByIA:JobApp_AppliedPosition      ${appliedpositionvalue}
    Input Text	    FindElementsByIA:JobApp_CoverLetter      ${coverlettervalue}
    Input Text	    FindElementsByIA:JobApp_TotalYearsOfExperience      ${yearsexperiencevalue}
    Click Element  FindElementsByIA:JobApp_ApplyButton
    Wait Until Element Is Visible       FindElementsByIA:JobApplicationForm_SuccessfullySubmittedMsg
    Log to Console  Job application complete
    Close Browser

TestParentSibling
    [Documentation]    Ce test ouvre une page web et récupère le contenu texte d'une cellule spécifique d'un tableau.
    [Tags]  AutomIA
    Add Location Strategy    FindElementsByIA    AutomIA Locator Strategy   ${True}
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/SiteParentSibling/ClimatologieMensuelle-Infoclimat.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Wait Until Page Contains Element    FindElementsByIA:table_StationMeteo    timeout=30s
    ${cell_text}=    Get Text    FindElementsByIA:cell_AIGUES-MORTES_TXM
    Log    Le texte de la cellule est: ${cell_text}
    Close Browser