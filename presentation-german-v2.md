# **Vibe coding**
## Wenn Software beginnt, Software zu schreiben

*the good, the bad and the ugly*

---

## me.introduce()

- Franz Faul, ZKB, ehem ZHAWler
- Mache vieles mit KI-gestützter und agentischer Entwicklung
- Interessiert, wie sich Softwareentwicklung verändert
- https://github.com/fauli
---

## Einstiegsfrage

**Wie viele von euch nutzen bereits Agents beim Programmieren?**

- 🟩 Regelmässig (1)
- 🟨 Ein paar Mal (2)
- 🟥 Nie (3)

💬 *Egal wie eure Antwort lautet — es wird für eure (Programmier-)Karriere relevant sein.*

---

## Agenda
*tbd with Merne: yes/no?*

1. 🔙 Geschichte — wie wir hierher kamen
2. 🧠 LLMs & Coding-Assistenten
3. 🤖 Von Assistenten → Agenten
4. 🧰 Aktuelle Tools & Beispiele
5. ⚠️ Herausforderungen, Risiken & Ethik
6. 🚀 Zukunft & eure Rolle

---

# Teil 1
## time.rewind()

---

## Von Lochkarten zu Prompts

Programmierung wird immer **abstrakter**:

- Maschinencode → Assembler
- C → Java → Frameworks
- Cloud → Container → DevOps
- KI-gestützte Programmierung

🧠 Jeder Schritt entfernt uns von Syntax hin zu Ideen.

---

## Die 3 Ären der Software (Karpathy)

| Ära | Beschreibung |
|------|------------|
| **Software 1.0** | Menschen schreiben Code |
| **Software 2.0** | Menschen trainieren Modelle (NNs = Code) |
| **Software 3.0** | Menschen schreiben *Ziele & Prompts* |

🔥 Heute befinden wir uns im Übergang von 2.0 → 3.0.

---

## Warum KI für Code?

Code ist:

- Strukturiert
- Repetitiv
- Öffentlich verfügbar (GitHub, Docs, StackOverflow)
- Hat Regeln und Muster

Perfektes Lernmaterial für grosse Sprachmodelle.

---

## Zeitstrahl: Wie wir hierher kamen

- 2010–2018 → Deep Learning Boom
- 2020 → GPT-3: erstes grosses allgemeines Sprachmodell
- 2022 → ChatGPT verleiht Coding-Superkräfte
- 2023–2025 → Agentische KI erscheint (AutoGPT, Devin, CrewAI)

---

# Teil 2
## LLMs & Coding-Assistenten

---

## Was ist ein LLM?

Ein Modell, das trainiert wurde, das **nächste Wort/Token vorherzusagen**.

Es lernt aus:

- Natürlicher Sprache
- Code-Repositories
- Dokumentation
- Mustern und Strukturen

⚙️ Kein menschliches Denken — aber mächtige Mustersynthese.

---

## Coding-Assistenten

Beispiele:

GitHub Copilot, ChatGPT, Cursor, Codeium

Sie können:

- Grundgerüste generieren
- Korrekturen vorschlagen
- Tests schreiben
- Unbekannten Code erklären

👉 Immer noch **reaktiv** — du fragst, es antwortet.

---

## Der neue (alte) Workflow

Alter Weg:

```

Google → StackOverflow → kopieren/einfügen → debuggen → wiederholen

```

Neuer Weg:

```

Absicht beschreiben → KI entwirft → Du prüfst → iterieren

```

Du wechselst vom **Code tippen** zum **über Code nachdenken**.

---

# Teil 3
## Von Assistenten zu Agenten

---

## Was ist ein KI-Agent?

> 🚀 **Ein Agent ist ein KI-System, das ein Ziel autonom verfolgen kann, indem es Werkzeuge, Gedächtnis und Feedback-Schleifen nutzt.**

Im Gegensatz zu Assistenten können Agenten:

*Planen, Ausführen, Beobachten und bewerten, Iterieren*

---

## Assistent vs Agent

| Merkmal | Assistent | Agent |
|--------|-----------|--------|
| Input | Prompt | Ziel |
| Verhalten | Eine Antwort | Mehrstufige Schleife |
| Gedächtnis | Kurz | Langzeit + kontextuell |
| Werkzeuge | Begrenzt | Kann Code, Tests, Browser, Repo ausführen |
| Autonomie | Niedrig | Mittel–Hoch |

---

## Let the vibin' begin!

1. 🎯 Ziel erhalten
2. 🧩 Schritte planen
3. 🛠️ Aktionen ausführen
4. 👀 Ergebnisse beobachten
5. 🔁 Reflektieren & anpassen
6. 🏁 Wiederholen bis fertig

---

## Anatomie eines Coding-Agenten

- 🧠 **LLM-Gehirn**
- 🧰 **Werkzeug-Schicht** (Dateisystem, CLI, Browser, APIs)
- 💾 **Gedächtnis** (Kontext + Vektorspeicher)
- 🗂️ **Orchestrierungs-Framework** (LangChain, CrewAI, ReAct)

---

# Teil 4
## Aktuelle Tools & Beispiele

---

## Ökosystem-Überblick (2025)

- AutoGPT / BabyAGI *(frühe Prototypen)*
- LangChain *(allgemeines Agenten-Framework)*
- CrewAI *(Multi-Agenten-Kollaboration)*
- OpenDevin / Devin *(autonome Softwareentwicklung)*

Der Bereich entwickelt sich *schnell.*

---

## "KI-Software-Ingenieur" Beispiele

"Fähigkeiten":

- Ein Repository verstehen
- Features planen
- Mehrere Dateien bearbeiten
- Tests ausführen
- Pull Requests erstellen

👉 Erfordert immer noch menschliche Überprüfung — denkt an **Praktikant**, nicht Senior-Entwickler.

---

## Beispiel: Echte Aufgabe

> "Füge Logging zu allen API-Endpunkten hinzu und gib standardisiertes Fehler-JSON zurück."

- Scannt Repository
- Schlägt Plan vor
- Ändert mehrere Dateien
- Führt Tests aus
- Iteriert basierend auf Fehlern

---

# Teil 5
## 🥁 The ugly

---

## Wo Agenten scheitern

- Halluzinierte oder falsche Lösungen
- Sehr verboser code
- Ähnliche Lösungen an verschiedenen Orten
- Falsches Selbstvertrauen
- Mangelndes Domänenwissen
- Überanpassung an Muster statt echtem Denken

---

## Sicherheit & Zuverlässigkeit

- Sicherheitslücken
- Abhängigkeiten werden unbemerkt eingefügt
- Lizenz-Unklarheiten
- Unsichere Muster werden blind kopiert

🛑 Vertrauen — aber überprüfen.

---

## Mensch in der Schleife

Ihr seid weiterhin verantwortlich für:

- Architektur
- Code-Review
- Testing
- Produktionsqualität
- Ethik & Sicherheit

👩‍💻 Agenten beschleunigen **Engineering** — sie ersetzen es nicht.

---

# Teil 6
## Die Zukunft & Eure Rolle

---

## Was kommt als Nächstes?

- Repository-bewusste Agenten
- Multi-Agenten-Teams (Architekt + Coder + Tester)
- Kontinuierlich selbstwartende Codebasen
- "Vibe Coding" — beschreibe das *Gefühl*, nicht die Syntax

---

## Welche Fähigkeiten zählen jetzt?

- Problemlösung
- Systemdesign
- Code lesen und validieren
- Absichten klar kommunizieren
- Trade-offs & Architektur verstehen

KI schreibt schneller — aber *ihr* entscheidet, **was geschrieben werden soll.**

---

# Fragen & Ressourcen

📚 Empfohlene Wege:

- LangChain / CrewAI Tutorials
- Karpathy: Software 2.0 und 3.0
- Probiert KI für euer nächstes Projekt — aber überprüft alles.

---

## Danke ✨

Bereit, die Zukunft des Programmierens zu erkunden?

