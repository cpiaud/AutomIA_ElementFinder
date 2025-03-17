import re
import Levenshtein
from difflib import SequenceMatcher
from collections import Counter
from math import sqrt


def est_une_regex(pattern):
    try:
        re.compile(pattern)     # Try compiling the pattern
        return True      # If it passes, it's a valid regex
    except re.error:
        return False     # Error = this is not a valid regex

# Tests
# print(est_une_regex("\d{3}-\d{2}-\d{4}"))   # True (regex)
# print(est_une_regex("Banane - (\d+\.\d{1,2})€/kg"))   # True (regex)
# print(est_une_regex("Banane - 1.80€/kg"))   # True (c'est une chaîne valide en regex, même si ce n'est pas une regex "classique")
# print(est_une_regex("*banane"))             # False (car * au début est une erreur de syntaxe regex)


def similarity_coefficient(s1, s2):
    # Calcul du coefficient de similarité avec SequenceMatcher
    seq_match_coeff = SequenceMatcher(None, s1, s2).ratio()
    print(f"With Sequence Matcher, similarity coefficient is : {seq_match_coeff}")

    # Calcul du coefficient de similarité avec Levenshtein
    levenshtein_coeff = Levenshtein.ratio(s1, s2)
    print(f"With Levenshtein, similarity coefficient is : {levenshtein_coeff}")

    # Calcul du coefficient de similarité avec Jaccard
    set1, set2 = set(s1), set(s2)
    jaccard_coeff = len(set1 & set2) / len(set1 | set2)
    print(f"With Jaccard, similarity coefficient is : {jaccard_coeff}")

    # Calcul du coefficient de similarité avec Cosine
    vec1, vec2 = Counter(s1), Counter(s2)
    dot_product = sum(vec1[ch] * vec2[ch] for ch in vec1)
    magnitude1 = sqrt(sum(count ** 2 for count in vec1.values()))
    magnitude2 = sqrt(sum(count ** 2 for count in vec2.values()))
    cosine_coeff = dot_product / (magnitude1 * magnitude2)
    print(f"With Cosine, similarity coefficient is : {cosine_coeff}")

    coefficients = [seq_match_coeff, levenshtein_coeff, jaccard_coeff, cosine_coeff]

    # Calcul du coefficient de similarité avec Hamming (si les chaînes sont de même longueur)
    if len(s1) == len(s2):
        hamming_coeff = 1 - sum(c1 != c2 for c1, c2 in zip(s1, s2)) / len(s1)
        print(f"With Hamming, similarity coefficient is : {hamming_coeff}")
        coefficients.append(hamming_coeff)
    else:
        print("Hamming similarity cannot be calculated: strings must be of equal length.")

    average_coefficient = sum(coefficients) / len(coefficients)
    max_coefficient = max(coefficients)

    return average_coefficient, max_coefficient

# Exemple d'utilisation
if __name__ == "__main__":
    string1 = "Abonnement tutti illimité"
    string2 = "Forfait tutti illimité -25 ans"
    avg_coeff, max_coeff = similarity_coefficient(string1, string2)
    print(f"Average similarity coefficient is : {avg_coeff}")
    print(f"Maximum similarity coefficient is : {max_coeff}")

"""
string1 = "geeks"
string2 = "geeky"
With Sequence Matcher, similarity coefficient is : 0.8
With Levenshtein, similarity coefficient is : 0.8
With Jaccard, similarity coefficient is : 0.6
With Cosine, similarity coefficient is : 0.857142857142857
With Hamming, similarity coefficient is : 0.8
Average similarity coefficient is : 0.7714285714285714

string1 = "Banane - 1.80€/kg"
string2 = "Banane - 2.57€/kg"
With Sequence Matcher, similarity coefficient is : 0.8235294117647058
With Levenshtein, similarity coefficient is : 0.8235294117647058
With Jaccard, similarity coefficient is : 0.6470588235294118
With Cosine, similarity coefficient is : 0.8695652173913044
With Hamming, similarity coefficient is : 0.8235294117647058
Average similarity coefficient is : 0.7974424552429668

string1 = "Banane - 1.80€/kg"
string2 = "Orange - 1.80€/kg"
With Sequence Matcher, similarity coefficient is : 0.8235294117647058
With Levenshtein, similarity coefficient is : 0.8235294117647058
With Jaccard, similarity coefficient is : 0.8125
With Cosine, similarity coefficient is : 0.8645299348672513
With Hamming, similarity coefficient is : 0.7058823529411764
Average similarity coefficient is : 0.8059942222675678

string1 = "Banane - 11.57€/kg"
string2 = "Banane - 1.80€/kg"
With Sequence Matcher, similarity coefficient is : 0.8571428571428571
With Levenshtein, similarity coefficient is : 0.8571428571428572
With Jaccard, similarity coefficient is : 0.75
With Cosine, similarity coefficient is : 0.8996469021204839
Hamming similarity cannot be calculated: strings must be of equal length.
Average similarity coefficient is : 0.8409831541015496

string1 = "Banane - 11.57€/kg"
string2 = "Orange - 1.80€/kg"
With Sequence Matcher, similarity coefficient is : 0.6857142857142857
With Levenshtein, similarity coefficient is : 0.6857142857142857
With Jaccard, similarity coefficient is : 0.6111111111111112
With Cosine, similarity coefficient is : 0.7703288865196434
Hamming similarity cannot be calculated: strings must be of equal length.
Average similarity coefficient is : 0.6882171422648315
"""
