#!/usr/bin/env python3
"""Окказио — находит в русском тексте слова, которых нет в словаре.

Запуск:  python okkazio.py sample.txt
"""
import re
import sys
from collections import defaultdict

import pymorphy3

morph = pymorphy3.MorphAnalyzer()
WORD = re.compile(r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*")


def known(word):
    return morph.word_is_known(word)


def hint(word):
    """Ищет в слове две знакомые части: кофечай -> кофе + чай."""
    for i in range(3, len(word) - 2):
        left, right = word[:i], word[i:]
        stems = [left] + ([left[:-1]] if left[-1] in "ое" else [])
        for stem in stems:
            head = next((stem + e for e in ("", "о", "а", "ь") if known(stem + e)), None)
            if head and known(right):
                return f"{head} + {right}"
    return ""


def is_sentence_start(text, pos):
    before = text[:pos].rstrip(" «\"—-(")
    return not before or before[-1] in ".!?…\n:"


def find_candidates(text):
    seen = defaultdict(list)
    for m in WORD.finditer(text):
        word = m.group()
        if word[0].isupper() and not is_sentence_start(text, m.start()):
            continue  # скорее всего имя собственное
        seen[word.lower()].append(m)

    result = []
    for word, hits in seen.items():
        if len(word) < 5 or known(word):
            continue
        if "-" in word and all(known(p) for p in word.split("-") if len(p) > 3):
            continue  # обычный дефисный композит вроде «диван-кровать»
        m = hits[0]
        context = re.sub(r"\s+", " ", text[max(0, m.start() - 40): m.end() + 40])
        result.append((word, len(hits), hint(word), context))

    # сначала слова с гипотезой, затем редкие
    return sorted(result, key=lambda r: (not r[2], r[1], r[0]))


def main():
    if len(sys.argv) < 2:
        sys.exit("Использование: python okkazio.py файл.txt")
    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    candidates = find_candidates(text)
    print(f"Кандидатов в окказионализмы: {len(candidates)}\n")
    for word, count, guess, context in candidates:
        print(f"• {word}  (×{count})" + (f"  ← {guess}" if guess else ""))
        print(f"    …{context.strip()}…\n")


if __name__ == "__main__":
    main()
