*** Settings ***
Documentation       Scenario de navigation par CLICS, compare a chaque etape le
...                 rendu entre deux versions de Firefox (pilotees en parallele).
...
...                 On ouvre le site dans les deux versions, on clique sur des
...                 boutons/liens avec des keywords Selenium, et a chaque etape on
...                 verifie que le rendu ne diverge pas au-dela du seuil. Un
...                 result.json est ecrit par etape dans ${CAPTURES_DIR}/<etape>/.
...
...                 Lancer :
...                 robot --outputdir output/robot tests/interactive_navigation.robot

# Chemin relatif au .robot.
Library             ${CURDIR}/../resources/keywords/ScreenshotCompareLibrary.py

Suite Teardown      Close Versions


*** Variables ***
${SITE}             https://anathos.me/
${FIREFOX_A}        /usr/bin/firefox
${FIREFOX_B}        ${CURDIR}/../firefoxes/firefox-128esr/firefox
${CAPTURES_DIR}     ${CURDIR}/../output/interactive
# Storage state (cookies + localStorage) produit par tests/capture_auth.robot.
${AUTH_FILE}        ${CURDIR}/../resources/env/auth.json
# % de difference au-dela duquel une etape echoue.
${FAIL_OVER}        ${5.0}


*** Test Cases ***
Naviguer Par Clics Et Comparer A Chaque Etape
    [Documentation]    3 etapes : accueil -> clic Photographie -> retour + clic bouton langue.
    Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
    Load Storage State    ${AUTH_FILE}

    Verifier L'Etape    accueil

    Click Element    css=a[href="/photographie"]
    Verifier L'Etape    apres-clic-photographie

    Go Back
    Click Element    css=a[href="/en"]
    Verifier L'Etape    apres-clic-bouton-langue


*** Keywords ***
Verifier L'Etape
    [Documentation]    Capture l'etat courant des 2 versions et echoue au-dela de ${FAIL_OVER} %.
    [Arguments]    ${nom}
    ${pct}=    Capture And Compare    ${nom}    ${CAPTURES_DIR}
    Log    ${nom} -> ${pct} %    console=${True}
    Should Be True    ${pct} <= ${FAIL_OVER}
    ...    msg=Etape '${nom}' : ${pct} % de difference (seuil ${FAIL_OVER} %)
