*** Settings ***
Resource   ../resources/CustomKeywords.robot
Suite Setup  Add Location Strategy    FindElementsByIA    AutomIA Locator Strategy   ${True}  


*** Variables ***
${BROWSER}    edge
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

*** Test Cases ***
Test Classic V1
    TestClassic       SiteDemoOriginal

Test Avec AutomIA V1
    TestAvecAutomIA   SiteDemoOriginal

Test Classic V2 
    TestClassic       SiteDemoEvoTexte

Test Avec AutomIA V2
    TestAvecAutomIA   SiteDemoEvoTexte

Test Classic V3
    TestClassic       SiteDemoEvoTech

Test Avec AutomIA V3
    TestAvecAutomIA   SiteDemoEvoTech

Test Classic V4
    TestClassic       SiteDemoRefonte

Test Avec AutomIA V4
    TestAvecAutomIA   SiteDemoRefonte

TestParentSibling
    [Documentation]    Ce test ouvre une page web et récupère le contenu texte d'une cellule spécifique d'un tableau.
    [Tags]  AutomIA
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/SiteParentSibling/ClimatologieMensuelle-Infoclimat.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Wait Until Page Contains Element    FindElementsByIA:table_StationMeteo    timeout=30s
    ${cell_text}=    Get Text    FindElementsByIA:cell_AIGUES-MORTES_TXM
    Log    Le texte de la cellule est: ${cell_text}
    Close Browser

TestDynamicAttributAutomIA
    [Tags]  AutomIA
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/SiteDemoOriginal/Login.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Log to Console  login
    Wait Until Element Is Visible       FindElementsByIA:login_username_var|textContent:User Name|index:6
    Input Text      FindElementsByIA:login_username_var  ${username}
    Input Text      FindElementsByIA:login_password  ${password}
    Click Element   FindElementsByIA:login_ConnexionButton
    Log to Console  job application form
    Close Browser

*** Keywords ***
TestClassic
    [Arguments]  ${siteDemo}
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
    [Arguments]  ${siteDemo}
    [Tags]  AutomIA
    #Set Selenium Speed  0.2
    ${loginpageurl}=    Set Variable    file:///${CURDIR}/${siteDemo}/Login.html
    Log    New url: ${loginpageurl}
    Open Browser        ${loginpageurl}     ${BROWSER}
    Maximize Browser Window
    Log to Console  login
    Wait Until Element Is Visible       FindElementsByIA:login_username
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
