*** Settings ***
Documentation       Ouvre le site avec le Firefox systeme (fenetre visible),
...                 laisse le temps de se connecter, puis enregistre le storage
...                 state (cookies + localStorage) dans resources/env/auth.json.
...
...                 Ce fichier est ensuite reutilise par
...                 tests/interactive_navigation.robot (keyword Load Storage
...                 State) pour comparer les 2 versions en session authentifiee.
...
...                 Lancer :
...                 robot --outputdir output/robot tests/capture_auth.robot

Library             ${CURDIR}/../resources/keywords/ScreenshotCompareLibrary.py


*** Variables ***
${SITE}             https://anathos.me/
${FIREFOX}          /usr/bin/firefox
${AUTH_FILE}        ${CURDIR}/../resources/env/auth.json
# Fenetre visible par defaut pour pouvoir se connecter a la main.
${HEADLESS}         ${False}
# Secondes laissees pour se connecter avant la capture.
${LOGIN_WAIT}       ${20}


*** Test Cases ***
Capturer Le Storage State
    [Documentation]    Connecte-toi dans la fenetre ouverte pendant l'attente.
    Open Auth Browser    ${SITE}    ${FIREFOX}    headless=${HEADLESS}
    Log    Connecte-toi maintenant (${LOGIN_WAIT}s) puis attends la capture.    console=${True}
    Sleep    ${LOGIN_WAIT}s
    Save Storage State    ${AUTH_FILE}
    [Teardown]    Close Auth Browser
