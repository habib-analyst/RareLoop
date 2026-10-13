"""Curated medical knowledge: suspected condition -> specialties & signals.

This is a small, hand-built knowledge base of rare conditions chosen because
patients commonly struggle to find the right specialist for them (the core
problem RareLoop addresses). It is deliberately conservative:

- aliases are symptom phrases used for keyword matching (no diagnosis),
- specialties are ordered by typical diagnostic ownership,
- the agent always presents this as "worth discussing with a clinician".

NOT a diagnostic engine. See disclaimer.py.
"""

CONDITIONS = {
    "ehlers-danlos": {
        "name": "Ehlers-Danlos syndrome (hypermobile type)",
        "aliases": [
            "ehlers", "eds", "hypermobile", "double-jointed", "double jointed",
            "dislocat", "sublux", "stretchy skin", "bendy", "joint pain",
            "loose joints", "fragile skin",
        ],
        "specialties": ["Rheumatology", "Medical Genetics"],
        "tag_slugs": ["ehlers-danlos", "hypermobility"],
        "questions": [
            "Which diagnostic criteria do you use for hypermobile EDS, and how do you rule out mimics?",
            "How many patients with EDS or hypermobility spectrum disorders do you currently follow?",
            "What does long-term monitoring look like (joints, cardiac, autonomic symptoms)?",
        ],
    },
    "marfan": {
        "name": "Marfan syndrome",
        "aliases": [
            "marfan", "tall stature", "long arms", "arachnodactyly",
            "lens dislocation", "dislocated lens", "ectopia lentis",
            "aortic", "aorta", "dilated aortic root",
        ],
        "specialties": ["Cardiology", "Medical Genetics"],
        "tag_slugs": ["marfan", "aortic-aneurysm"],
        "questions": [
            "Do you run a dedicated aortic surveillance program with scheduled imaging?",
            "At what aortic diameter would you refer for surgical evaluation?",
            "Do you coordinate family screening for first-degree relatives?",
        ],
    },
    "cystic-fibrosis": {
        "name": "Cystic fibrosis",
        "aliases": [
            "cystic fibrosis", "salty skin", "salty sweat", "thick mucus",
            "recurrent chest infections", "chronic cough", "bronchiectasis",
            "failure to thrive", "meconium ileus",
        ],
        "specialties": ["Pulmonology", "Medical Genetics"],
        "tag_slugs": ["cystic-fibrosis", "bronchiectasis"],
        "questions": [
            "Can you arrange sweat-chloride testing and CFTR genetic testing?",
            "Do you offer airway-clearance and physiotherapy programs?",
            "Are CFTR modulator therapies accessible through your practice?",
        ],
    },
    "duchenne": {
        "name": "Duchenne muscular dystrophy",
        "aliases": [
            "duchenne", "gower", "gowers", "calf pseudohypertrophy",
            "large calves", "calves", "climb up", "muscle weakness child",
            "waddling gait", "difficulty climbing stairs", "dystrophin",
        ],
        "specialties": ["Pediatric Neurology", "Neurology"],
        "tag_slugs": ["duchenne", "neuromuscular"],
        "questions": [
            "What is your diagnostic pathway — CK, MLPA/dystrophin genetics, muscle biopsy?",
            "Do you coordinate cardiac and respiratory surveillance as recommended for DMD?",
            "Are there clinical trials or exon-skipping therapies you can refer to?",
        ],
    },
    "gaucher": {
        "name": "Gaucher disease",
        "aliases": [
            "gaucher", "enlarged spleen", "splenomegaly", "enlarged liver",
            "hepatosplenomegaly", "low platelets", "thrombocytopenia",
            "bone pain", "bone crisis", "glucocerebrosidase",
        ],
        "specialties": ["Hematology", "Medical Genetics"],
        "tag_slugs": ["gaucher", "lysosomal-storage", "ert"],
        "questions": [
            "Can you order beta-glucocerebrosidase enzyme activity and GBA genetic testing?",
            "Do you manage enzyme replacement or substrate reduction therapy?",
            "How do you monitor bone disease and spleen/liver volumes over time?",
        ],
    },
    "fabry": {
        "name": "Fabry disease",
        "aliases": [
            "fabry", "burning pain hands", "burning pain feet", "acroparesthesia",
            "angiokeratoma", "dark red spots", "heat intolerance",
            "can't sweat", "cannot sweat", "anhidrosis", "proteinuria",
            "alpha-galactosidase",
        ],
        "specialties": ["Nephrology", "Medical Genetics"],
        "tag_slugs": ["fabry", "lysosomal-storage", "proteinuria"],
        "questions": [
            "Can you arrange alpha-galactosidase A activity and GLA gene testing?",
            "How do you monitor renal and cardiac involvement in Fabry patients?",
            "Do you coordinate enzyme replacement or chaperone therapy?",
        ],
    },
    "narcolepsy": {
        "name": "Narcolepsy type 1",
        "aliases": [
            "narcolepsy", "excessive daytime sleepiness", "fall asleep suddenly",
            "cataplexy", "knees buckle", "muscle weakness laughing",
            "sleep paralysis", "hypnagogic hallucinations",
        ],
        "specialties": ["Sleep Medicine", "Neurology"],
        "tag_slugs": ["narcolepsy", "cataplexy", "polysomnography"],
        "questions": [
            "Do you perform in-lab polysomnography followed by MSLT for diagnosis?",
            "How do you manage cataplexy alongside daytime sleepiness?",
            "What is the follow-up schedule once treatment starts?",
        ],
    },
    "behcet": {
        "name": "Behcet's disease",
        "aliases": [
            "behcet", "behçet", "mouth ulcers", "oral ulcers", "genital ulcers",
            "genital sores", "uveitis", "eye inflammation", "pathergy",
        ],
        "specialties": ["Rheumatology", "Ophthalmology"],
        "tag_slugs": ["behcet", "vasculitis", "uveitis"],
        "questions": [
            "How do you distinguish Behcet's from other causes of recurrent ulcers and uveitis?",
            "Do you co-manage eye involvement with an ophthalmologist?",
            "When do you escalate from colchicine to immunosuppression or biologics?",
        ],
    },
    "myasthenia-gravis": {
        "name": "Myasthenia gravis",
        "aliases": [
            "myasthenia", "drooping eyelid", "droop", "ptosis", "double vision",
            "diplopia", "fluctuating weakness", "weakness worse evening",
            "difficulty swallowing", "dysphagia", "thymoma",
            "comes back with rest", "better with rest", "recovers with rest",
            "after rest",
        ],
        "specialties": ["Neurology"],
        "tag_slugs": ["myasthenia-gravis", "emg", "neuroimmunology"],
        "questions": [
            "Which antibody panels and electrodiagnostic tests do you use to confirm MG?",
            "How do you decide between symptomatic therapy, immunosuppression and thymectomy referral?",
            "What is your protocol for myasthenic crisis — do you have ICU pathways?",
        ],
    },
    "wilson": {
        "name": "Wilson's disease",
        "aliases": [
            "wilson", "kayser-fleischer", "brown rings cornea", "corneal rings",
            "tremor", "parkinsonism young", "liver failure young",
            "hemolytic anemia", "ceruloplasmin", "atp7b",
        ],
        "specialties": ["Hepatology", "Neurology", "Medical Genetics"],
        "tag_slugs": ["wilson", "liver"],
        "questions": [
            "Can you arrange ceruloplasmin, 24-hour urinary copper and ATP7B testing?",
            "How do you monitor chelation therapy and watch for overtreatment?",
            "Do you screen siblings and family members once diagnosed?",
        ],
    },
}

# Symptom phrases that trigger emergency guidance INSTEAD of specialist matching.
# Conservative on purpose: false positives cost a warning, false negatives cost lives.
RED_FLAG_PATTERNS = [
    "chest pain", "crushing chest", "pressure in chest", "tight chest",
    "heart attack", "can't breathe", "cannot breathe", "difficulty breathing",
    "shortness of breath", "stroke", "face droop", "slurred speech",
    "weakness one side", "suicidal", "kill myself", "end my life",
    "unconscious", "fainted and", "severe bleeding", "coughing blood",
    "overdose", "poisoning",
]


def match_condition(text: str):
    """Return (condition_key, matched_alias_phrases) for the best-matching
    condition, or (None, []) if nothing matches."""
    t = text.lower()
    best, best_hits = None, []
    for key, cond in CONDITIONS.items():
        hits = sorted({a for a in cond["aliases"] if a in t}, key=len, reverse=True)
        # de-duplicate overlapping aliases (e.g. "eds" inside a longer hit)
        deduped = []
        for h in hits:
            if not any(h != k and h in k for k in deduped):
                deduped.append(h)
        if len(deduped) > len(best_hits):
            best, best_hits = key, deduped
    return best, best_hits


def find_red_flags(text: str):
    t = text.lower()
    return [p for p in RED_FLAG_PATTERNS if p in t]
