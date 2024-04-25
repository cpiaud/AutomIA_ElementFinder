*** Settings ***
Library  SeleniumLibrary
Library  OperatingSystem

*** Variables ***
${loginButton}  xpath://a[text()='Connexion']
${userText}  name:email
${passwordText}  name:pass

*** Keywords ***
login
    [Arguments]  ${username}  ${pw}
    Log to Console  login
    Wait Until Element Is Visible  ${userText}
    Input Text  ${userText}  ${username}
    Input Text  ${passwordText}  ${pw}
    Click Element  ${loginButton}