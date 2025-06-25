# AutomIA - Custom Locator Robot Framework

AutomIA est une librairie qui permet d'utiliser un locator personnalisé dans Robot Framework pour localiser des éléments web via un fichier JSON et une stratégie de recherche intelligente.

## 📦 Installation

1. Télécharger le repo : [AutomIA_ElementFinder](https://github.com/cpiaud/AutomIA_ElementFinder/archive/refs/heads/main.zip)
2. Copier le répertoire `resources` à la racine de votre projet
3. Copier `requirements.txt` à la racine de votre projet
4. Installer les dépendances Python :

   ```bash
   pip install -r requirements.txt
   ```

5. Configurer le fichier `resources/settings.yaml` :
   - Chemin vers le répertoire `objectrepository`
   - Nom personnalisé de la librairie Selenium (si applicable)

6. Dans chaque fichier `.robot` où vous souhaitez utiliser AutomIA, ajoutez :

   ```robot
   *** Settings ***
   Resource    ../resources/CustomKeywords.robot
   Suite Setup    Add Location Strategy    FindElementsByIA    AutomIA Locator Strategy    ${True}
   ```

   ⚠️ Adaptez le chemin si vos fichiers de test sont dans des sous-répertoires plus profonds.

---

## 🚀 Première utilisation

1. **Récupérer les éléments Web avec l'espion** :
   - Télécharger [spyon.js](https://github.com/cpiaud/AutomIA_SpyWeb/blob/master/spyon.js)
   - Ouvrir la console navigateur (F12), coller le script et valider
   - Survolez les éléments pour voir leurs attributs/frères/parents
   - Clic droit sur l'élément à enregistrer dans le `objectrepository`

2. **Utilisation dans un test** :

   ```robot
   # Avant
   Click Element    locator=${locator_bouton_consulter_dossier}

   # Avec AutomIA
   Click Element    FindElementsByIA:bouton_consulter_dossier
   ```

---

## 📊 Syntaxe

```text
<Action Keyword>    FindElementsByIA:<Element File Name>|<Attribut Name>:<Attribut Value>|...|elementNumber:<integer>
```

### 💡 Eléments de la syntaxe

| Terme | Description |
|-------|-------------|
| `<Action Keyword>` | Mot-clé RF comme `Click Element`, `Input Text` |
| `FindElementsByIA` | Clé de localisation personnalisée obligatoire |
| `<Element File Name>` | Fichier JSON dans `objectrepository` (sans `.json`) |
| `<Attribut Name>:<Attribut Value>` | Un ou plusieurs attributs HTML ou personnalisés |
| `elementNumber:<n>` | (optionnel) Numéro de l'élément à utiliser si plusieurs sont trouvés |

### 📅 Exemples valides

```robot
# Usage basic
Wait Until Element Is Visible    FindElementsByIA:login_username
# Surcharge de la valeur d'un attribut (textContent)
Wait Until Element Is Visible    FindElementsByIA:login_username|textContent:User Name
# Surcharge de la valeur de 2 attributs (textContent et class)
Wait Until Element Is Visible    FindElementsByIA:login_username|textContent:User Name|class:px-0 ng-star
# Utilisation d'une expression régulière (Banane suivit de son prix)
Click Element    FindElementsByIA:li_Banane|textContent:Banane - (\d+\.\d{1,2})€/kg
# Passage d'une variable pour surcharger la valeur d'un attribut (textContent)
Input Text    FindElementsByIA:input_Quantity|textContent:${fruit}
# Forçage de l'utilisation d'un élément par son numéro d'ordre si plusieurs éléments identiques sont retournés (ex element 3 de la liste)
Input Text    FindElementsByIA:input_Quantity|elementNumber:3
```

---

## 📚 Organisation de l'`objectrepository`

- Vous pouvez créer des sous-dossiers.
- ❌ **Les fichiers JSON doivent être nommés de manière unique** (même en sous-dossiers)
- La recherche est **récursive** : le premier fichier trouvé avec le bon nom sera utilisé

Ce choix vise à simplifier l'écriture de la syntaxe `FindElementsByIA:nom_element`

---

## ⚙️ Fonctionnalités

### ➡️ Algorithme de recherche

1. **Tag** HTML
2. **Attributs** (id, name, class, textContent, etc.)
3. **Siblings** (frères)
4. **Ancestors** (parents) : analyse du `textContent`

Le poids des attributs est configurable via `resources/attributesWeight.properties`

### 🔎 Recherche textuelle (textContent)

- Texte exact
- Texte contenant la valeur
- Expression régulière valide
- Recherche floue (similarité ≥ 0.82 par défaut) → modifiable via `settings.yaml > SimilarityCoefficientMin`

---

## ❓ Si plusieurs éléments sont trouvés ?

Comportement défini par `continueOnMultipleElement` dans `settings.yaml` :

- `true` : Prend le **premier élément** pour effectuer l'action en cours
- `false` : Lève une **erreur explicite** pour signaler que plusieurs éléments ont été trouvés

---

## 📊 Idées d'amélioration futures

- Permettre des noms de fichiers JSON identiques dans des sous-dossiers (avec chemin complet ?)

---

Pour toute question ou suggestion, n'hésitez pas à ouvrir une [issue](https://github.com/cpiaud/AutomIA_ElementFinder/issues) sur GitHub ✨
