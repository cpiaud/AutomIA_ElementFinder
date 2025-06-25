# 📌 Mot-clé `Strong` pour Robot Framework

Le mot-clé `Strong` est une surcouche de robustesse pour l’exécution de mots-clés Robot Framework. Il permet de **rejouer automatiquement** un mot-clé en cas d’échec, en assurant au préalable la stabilité du DOM.
C'est le complément idéal à AutomIA pour assurer une robustesse maximale à l'exécution de vos tests
Il est intégré depuis la V4 d'AutomIA dans le fichier `CustomKeywords.robot`

## 🔍 Objectif

> Exécuter un mot-clé donné de manière fiable en gérant automatiquement :
>
> - La stabilisation du DOM
> - Les erreurs transitoires (ex. : `StaleElementReferenceException`)
> - Le rejeu automatique jusqu’à `n` fois avec délai paramétré

## ✅ Avantages

- 🔁 **Auto-rejeu** en cas d’exception
- ⏱️ **Évite les `Sleep` ou `Wait Until` codés en dur**
- 🧱 **Amélioration significative de la robustesse** des tests
- 💡 **Centralisation de la gestion d'attente et de fiabilité**

## 🔧 Syntaxe

```robot
Strong    <NomDuMotClé>    [arguments...]
```

- `${mot_cle}` : Le mot-clé Robot à exécuter (ex. `Click Element`)
- `@{args}` : Tous les arguments attendus par le mot-clé

## 🔁 Fonctionnement interne

Le mot-clé `Strong` repose sur :

1. `Attendre Que Le DOM Soit Stable` : attend la stabilité structurelle du DOM
2. Une boucle avec rejeu (`FOR ... TRY ... EXCEPT`) jusqu’à 10 fois (configurable si besoin)
3. Un `Sleep` court entre chaque tentative

En cas de succès, le mot-clé s'arrête immédiatement. En cas d'échec répété, une erreur explicite est levée.

## 📦 Mots-clés internes associés

### `Attendre Que Le DOM Soit Stable`

```robot
Attendre Que Le DOM Soit Stable
    [Documentation] Attend que le nombre d'éléments du DOM ne varie plus.
```

Utilisé pour détecter la stabilité structurelle du DOM avant d’interagir avec la page.

### `Attendre Que Le Texte Soit Stable`

```robot
Attendre Que Le Texte Soit Stable
    [Documentation] Attend que le texte visible de la page n’évolue plus entre deux instants.
```

Utile dans certains cas dynamiques, mais moins fiable que la stabilité du DOM.

---

## 📘 Exemple d'utilisation

```robot
TestAvecAutomIA
    [Arguments]    ${siteDemo}
    [Tags]         AutomIA

    ${loginpageurl}=    Set Variable    file:///${CURDIR}/${siteDemo}/Login.html
    Open Browser         ${loginpageurl}    ${BROWSER}
    Maximize Browser Window

    Strong    Input Text      FindElementsByIA:login_username     ${username}
    Strong    Input Text      FindElementsByIA:login_password     ${password}
    Strong    Click Element   FindElementsByIA:login_ConnexionButton
```

> Ici, chaque interaction est encapsulée avec `Strong`, garantissant leur exécution même dans un contexte DOM dynamique ou lent.

---

## ⚙️ Paramètres par défaut

| Paramètre         | Valeur        | Description                                      |
|-------------------|---------------|--------------------------------------------------|
| `tentatives_max`  | `10`          | Nombre maximum de tentatives                    |
| `attente`         | `0.1s`        | Délai entre deux tentatives                     |
| `locator_racine`  | `xpath=//*`   | Racine pour le comptage DOM (peut être ciblé)   |

---

## 🧪 Cas typiques d'erreurs gérées

- `StaleElementReferenceException`
- DOM instable lors du clic ou remplissage
- Lenteur temporaire du chargement des éléments
- Transitions JS non terminées

---

## 🔎 Pour aller plus loin

- Ajouter une option pour passer dynamiquement les `tentatives_max` et le `temps d'attente`
- Ajouter une vérification de `readyState` si nécessaire

---

## 📂 Emplacement

Le mot-clé `Strong` peut être placé dans une `resource.robot` dédiée à la résilience, par exemple :

``` bash
resources/
├── keywords/
│   └── robustesse.robot  ← contient Strong et ses dépendances
```

---

## 📢 Remarque

> Ce mot-clé est particulièrement recommandé pour stabiliser les tests d'interface (IHM web) dans des environnements instables (CI/CD, navigateurs headless, applications dynamiques).
