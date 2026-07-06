*** Settings ***
Documentation       Compare le rendu d'un site entre deux versions de Firefox,
...                 un test distinct par page.
...
...                 Les pages sont decouvertes au crawl par le pre-run modifier
...                 PerPageModifier, qui remplace le test placeholder ci-dessous
...                 par un test par page. Un fichier result.json est ecrit par
...                 page dans ${CAPTURES_DIR}/<slug>/.
...
...                 Lancer :
...                 robot --prerunmodifier PerPageModifier.py:https://anathos.me/:20
...                 ...    --outputdir output/robot tests/firefox_versions.robot

Library             ${CURDIR}/../ScreenshotCompareLibrary.py


*** Variables ***
# -- parametres de COMPARAISON (utilises par le keyword) --
${FIREFOX_A}        /usr/bin/firefox
${FIREFOX_B}        ${CURDIR}/../firefoxes/firefox-128esr/firefox
${CAPTURES_DIR}     ${CURDIR}/../output/crawl
${WIDTH}            ${1280}
${HEIGHT}           ${900}
${WAIT}             ${2}
${THRESHOLD}        ${20}
# % de difference au-dela duquel une page (donc son test) echoue.
${FAIL_OVER}        ${5.0}


*** Test Cases ***
Placeholder (remplace au runtime par un test par page)
    [Documentation]    Ne s'execute que si le pre-run modifier n'est pas actif.
    Fail    Lance la suite avec --prerunmodifier PerPageModifier.py:<URL>:<MAX_PAGES>


*** Keywords ***
Compare One Page
    [Documentation]    Compare une page entre les 2 versions ; echoue au-dela de ${FAIL_OVER} %.
    [Arguments]    ${url}
    ${pct}=    Compare Page Across Versions    ${url}    ${FIREFOX_A}    ${FIREFOX_B}    ${CAPTURES_DIR}
    ...    width=${WIDTH}    height=${HEIGHT}    wait=${WAIT}    threshold=${THRESHOLD}
    Log    ${url} -> ${pct} %    console=${True}
    Should Be True    ${pct} <= ${FAIL_OVER}
    ...    msg=${url} : ${pct} % de difference (seuil ${FAIL_OVER} %)
