# Hospital Diagnosis Knowledge Repository

A knowledge repository for a real-world business system: **Medical Diagnosis and
Treatment Recommendation** in a hospital. It organises the knowledge base built in
Knowledge Engineering Experiment 1 (and the decision rules from Experiment 2) into
structured JSON files that can be versioned with Git and shared through GitHub.

## Repository structure

| File | Knowledge category |
|------|--------------------|
| `entity_definitions.json` | The 6 entities (Patient, Disease, Symptom, Doctor, Treatment, Department) and their attributes |
| `disease_knowledge.json` | Diseases with category, severity, contagiousness, recovery time |
| `symptom_knowledge.json` | Symptoms with body part, severity, duration |
| `treatment_knowledge.json` | Treatments with type, cost, duration |
| `doctor_department_knowledge.json` | Doctors and hospital departments |
| `relationship_knowledge.json` | Relationships between entities and their mappings |
| `diagnosis_rules.json` | Production rules R1-R6 (symptoms -> disease) |
| `decision_rules.json` | Decision rules D1-D9 (treatment, referral, admission, precautions) |
| `repository_tools.py` | Python tool to load, validate and search the repository |

## How to use

```
python repository_tools.py                 # validate all files and show a summary
python repository_tools.py search malaria  # keyword search across the repository
```

## Maintaining the knowledge

Every JSON file has `domain`, `category` and `version` fields. When a rule or fact
changes, edit the relevant file, increase its `version`, and commit the change with
a short message so the history of the knowledge is preserved.

> This repository is for academic purposes only and is not for real clinical use.
