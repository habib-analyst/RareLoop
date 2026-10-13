"""Realistic MOCK Qloo entity data for the rare-disease specialist finder.

Every record below is FICTIONAL sample data used only while no QLOO_API_KEY
is set. Records are shaped like normalized Qloo place entities (see
qloo_client.normalize_entity) so the agent, ranker and explainers behave
identically in mock and live modes.

Fields:
  entity_id  — mock URN (real Qloo ids look like opaque hex strings)
  name       — display name
  type       — always "urn:entity:place" (clinics/practices are places)
  properties — address, city, country, specialty, rating, review_count
  tags       — Qloo-style tags: [{"id": "urn:tag:mock:<slug>", "name": ...}]
  popularity — 0..1 entity popularity signal
  affinity   — 0..1 taste/affinity score from the insights call
  blurb      — short human-readable focus description
"""

SPECIALISTS = [
    {
        "entity_id": "mock:place:001",
        "name": "Dr. Ayesha Khan — Rheumatology & Hypermobility Clinic",
        "type": "urn:entity:place",
        "properties": {
            "address": "12-B Main Boulevard, Gulberg III, Lahore",
            "city": "Lahore", "country": "Pakistan",
            "specialty": "Rheumatology",
            "rating": 4.8, "review_count": 214,
        },
        "tags": [
            {"id": "urn:tag:mock:ehlers-danlos", "name": "Ehlers-Danlos syndrome"},
            {"id": "urn:tag:mock:hypermobility", "name": "Joint hypermobility"},
            {"id": "urn:tag:mock:autoimmune", "name": "Autoimmune disease"},
        ],
        "popularity": 0.82, "affinity": 0.91,
        "blurb": "Rheumatologist with a dedicated hypermobility clinic; manages "
                 "EDS workups, physiotherapy planning and pain programs.",
    },
    {
        "entity_id": "mock:place:002",
        "name": "Dr. Bilal Ahmed — Medical Genetics Centre",
        "type": "urn:entity:place",
        "properties": {
            "address": "44-C Shahrah-e-Faisal, Karachi",
            "city": "Karachi", "country": "Pakistan",
            "specialty": "Medical Genetics",
            "rating": 4.9, "review_count": 167,
        },
        "tags": [
            {"id": "urn:tag:mock:marfan", "name": "Marfan syndrome"},
            {"id": "urn:tag:mock:ehlers-danlos", "name": "Ehlers-Danlos syndrome"},
            {"id": "urn:tag:mock:genetic-counseling", "name": "Genetic counseling"},
        ],
        "popularity": 0.78, "affinity": 0.88,
        "blurb": "Clinical geneticist; connective-tissue disorder panels, family "
                 "screening and pre-symptomatic counseling.",
    },
    {
        "entity_id": "mock:place:003",
        "name": "Dr. Sarah Mitchell — Aortopathy & Connective Tissue Cardiology",
        "type": "urn:entity:place",
        "properties": {
            "address": "77 Harley Street, London",
            "city": "London", "country": "United Kingdom",
            "specialty": "Cardiology",
            "rating": 4.7, "review_count": 301,
        },
        "tags": [
            {"id": "urn:tag:mock:marfan", "name": "Marfan syndrome"},
            {"id": "urn:tag:mock:aortic-aneurysm", "name": "Aortic aneurysm surveillance"},
        ],
        "popularity": 0.85, "affinity": 0.84,
        "blurb": "Cardiologist specializing in heritable aortopathies; runs a "
                 "Marfan aortic surveillance program with annual imaging.",
    },
    {
        "entity_id": "mock:place:004",
        "name": "Dr. Faisal Raza — Pulmonology & Rare Lung Disease Unit",
        "type": "urn:entity:place",
        "properties": {
            "address": "F-8 Markaz, Islamabad",
            "city": "Islamabad", "country": "Pakistan",
            "specialty": "Pulmonology",
            "rating": 4.6, "review_count": 189,
        },
        "tags": [
            {"id": "urn:tag:mock:cystic-fibrosis", "name": "Cystic fibrosis"},
            {"id": "urn:tag:mock:bronchiectasis", "name": "Bronchiectasis"},
        ],
        "popularity": 0.74, "affinity": 0.86,
        "blurb": "Pulmonologist; sweat-chloride testing referrals, airway "
                 "clearance programs and CFTR modulator follow-up.",
    },
    {
        "entity_id": "mock:place:005",
        "name": "Dr. Nadia Hussain — Pediatric Neuromuscular Clinic",
        "type": "urn:entity:place",
        "properties": {
            "address": "9-A Model Town Link Road, Lahore",
            "city": "Lahore", "country": "Pakistan",
            "specialty": "Pediatric Neurology",
            "rating": 4.9, "review_count": 243,
        },
        "tags": [
            {"id": "urn:tag:mock:duchenne", "name": "Duchenne muscular dystrophy"},
            {"id": "urn:tag:mock:neuromuscular", "name": "Neuromuscular disorders"},
        ],
        "popularity": 0.88, "affinity": 0.93,
        "blurb": "Pediatric neurologist; dystrophinopathy diagnosis (MLPA, muscle "
                 "biopsy referral), steroid and physiotherapy management.",
    },
    {
        "entity_id": "mock:place:006",
        "name": "Dr. James Carter — Neuromuscular & EMG Laboratory",
        "type": "urn:entity:place",
        "properties": {
            "address": "55 Fruit Street, Boston, MA",
            "city": "Boston", "country": "United States",
            "specialty": "Neurology",
            "rating": 4.8, "review_count": 412,
        },
        "tags": [
            {"id": "urn:tag:mock:duchenne", "name": "Duchenne muscular dystrophy"},
            {"id": "urn:tag:mock:myasthenia-gravis", "name": "Myasthenia gravis"},
            {"id": "urn:tag:mock:emg", "name": "EMG / nerve conduction studies"},
        ],
        "popularity": 0.91, "affinity": 0.87,
        "blurb": "Neuromuscular neurologist with in-house EMG; manages myasthenia "
                 "gravis, muscular dystrophies and neuroimmunology therapies.",
    },
    {
        "entity_id": "mock:place:007",
        "name": "Dr. Imran Sheikh — Hematology & Lysosomal Storage Clinic",
        "type": "urn:entity:place",
        "properties": {
            "address": "DHA Phase 5, Karachi",
            "city": "Karachi", "country": "Pakistan",
            "specialty": "Hematology",
            "rating": 4.7, "review_count": 156,
        },
        "tags": [
            {"id": "urn:tag:mock:gaucher", "name": "Gaucher disease"},
            {"id": "urn:tag:mock:lysosomal-storage", "name": "Lysosomal storage disorders"},
            {"id": "urn:tag:mock:ert", "name": "Enzyme replacement therapy"},
        ],
        "popularity": 0.71, "affinity": 0.85,
        "blurb": "Hematologist; Gaucher and lysosomal storage workups, enzyme "
                 "assays and long-term ERT monitoring.",
    },
    {
        "entity_id": "mock:place:008",
        "name": "Dr. Maria Gonzalez — Nephrology & Inherited Kidney Disease",
        "type": "urn:entity:place",
        "properties": {
            "address": "20 Wimpole Street, London",
            "city": "London", "country": "United Kingdom",
            "specialty": "Nephrology",
            "rating": 4.6, "review_count": 198,
        },
        "tags": [
            {"id": "urn:tag:mock:fabry", "name": "Fabry disease"},
            {"id": "urn:tag:mock:proteinuria", "name": "Proteinuria workup"},
            {"id": "urn:tag:mock:lysosomal-storage", "name": "Lysosomal storage disorders"},
        ],
        "popularity": 0.76, "affinity": 0.83,
        "blurb": "Nephrologist; Fabry renal surveillance, proteinuria workups and "
                 "coordination of enzyme/chaperone therapy.",
    },
    {
        "entity_id": "mock:place:009",
        "name": "Dr. Tariq Mehmood — Sleep Disorders Centre",
        "type": "urn:entity:place",
        "properties": {
            "address": "Blue Area, Islamabad",
            "city": "Islamabad", "country": "Pakistan",
            "specialty": "Sleep Medicine",
            "rating": 4.5, "review_count": 132,
        },
        "tags": [
            {"id": "urn:tag:mock:narcolepsy", "name": "Narcolepsy"},
            {"id": "urn:tag:mock:cataplexy", "name": "Cataplexy"},
            {"id": "urn:tag:mock:polysomnography", "name": "Polysomnography / MSLT"},
        ],
        "popularity": 0.69, "affinity": 0.84,
        "blurb": "Sleep physician; in-lab polysomnography and MSLT for narcolepsy "
                 "diagnosis, cataplexy management.",
    },
    {
        "entity_id": "mock:place:010",
        "name": "Dr. Sana Malik — Rheumatology & Vasculitis Clinic",
        "type": "urn:entity:place",
        "properties": {
            "address": "Clifton Block 4, Karachi",
            "city": "Karachi", "country": "Pakistan",
            "specialty": "Rheumatology",
            "rating": 4.7, "review_count": 201,
        },
        "tags": [
            {"id": "urn:tag:mock:behcet", "name": "Behcet's disease"},
            {"id": "urn:tag:mock:vasculitis", "name": "Vasculitis"},
            {"id": "urn:tag:mock:uveitis", "name": "Uveitis (co-managed)"},
        ],
        "popularity": 0.79, "affinity": 0.86,
        "blurb": "Rheumatologist; systemic vasculitis including Behcet's, with "
                 "joint ophthalmology co-management for uveitis.",
    },
    {
        "entity_id": "mock:place:011",
        "name": "Dr. David Okafor — Uveitis & Ocular Inflammation Service",
        "type": "urn:entity:place",
        "properties": {
            "address": "243 Charles Street, Boston, MA",
            "city": "Boston", "country": "United States",
            "specialty": "Ophthalmology",
            "rating": 4.8, "review_count": 276,
        },
        "tags": [
            {"id": "urn:tag:mock:behcet", "name": "Behcet's disease"},
            {"id": "urn:tag:mock:uveitis", "name": "Uveitis"},
        ],
        "popularity": 0.83, "affinity": 0.82,
        "blurb": "Uveitis specialist; manages ocular Behcet's and coordinates "
                 "immunosuppression with rheumatology.",
    },
    {
        "entity_id": "mock:place:012",
        "name": "Dr. Hina Farooq — Hepatology & Metabolic Liver Clinic",
        "type": "urn:entity:place",
        "properties": {
            "address": "Johar Town, Lahore",
            "city": "Lahore", "country": "Pakistan",
            "specialty": "Hepatology",
            "rating": 4.6, "review_count": 178,
        },
        "tags": [
            {"id": "urn:tag:mock:wilson", "name": "Wilson's disease"},
            {"id": "urn:tag:mock:liver", "name": "Metabolic liver disease"},
        ],
        "popularity": 0.72, "affinity": 0.81,
        "blurb": "Hepatologist; Wilson's disease chelation monitoring, copper "
                 "studies and family screening.",
    },
    {
        "entity_id": "mock:place:013",
        "name": "Dr. Robert Chen — Medical Genetics & Genomic Medicine",
        "type": "urn:entity:place",
        "properties": {
            "address": "77 Avenue Louis Pasteur, Boston, MA",
            "city": "Boston", "country": "United States",
            "specialty": "Medical Genetics",
            "rating": 4.9, "review_count": 389,
        },
        "tags": [
            {"id": "urn:tag:mock:wilson", "name": "Wilson's disease"},
            {"id": "urn:tag:mock:fabry", "name": "Fabry disease"},
            {"id": "urn:tag:mock:gaucher", "name": "Gaucher disease"},
            {"id": "urn:tag:mock:wes", "name": "Whole-exome sequencing"},
        ],
        "popularity": 0.9, "affinity": 0.89,
        "blurb": "Clinical geneticist; exome/genome sequencing for undiagnosed "
                 "rare disease, variant interpretation and cascade testing.",
    },
    {
        "entity_id": "mock:place:014",
        "name": "Dr. Amina Yusuf — Neurology & Neuroimmunology",
        "type": "urn:entity:place",
        "properties": {
            "address": "PECHS Block 2, Karachi",
            "city": "Karachi", "country": "Pakistan",
            "specialty": "Neurology",
            "rating": 4.7, "review_count": 224,
        },
        "tags": [
            {"id": "urn:tag:mock:myasthenia-gravis", "name": "Myasthenia gravis"},
            {"id": "urn:tag:mock:emg", "name": "EMG / nerve conduction studies"},
            {"id": "urn:tag:mock:neuroimmunology", "name": "Neuroimmunology"},
        ],
        "popularity": 0.8, "affinity": 0.87,
        "blurb": "Neurologist; myasthenia gravis diagnosis (antibody panels, "
                 "repetitive nerve stimulation), thymectomy referral pathways.",
    },
]


def find_by_specialty(specialty: str):
    """Case-insensitive specialty lookup over the mock dataset."""
    s = specialty.strip().lower()
    return [e for e in SPECIALISTS if e["properties"]["specialty"].lower() == s]


def search_mock(query: str, city: str | None = None, take: int = 10):
    """Keyword search over names, specialties, tag names and blurbs."""
    q = query.lower().strip()
    scored = []
    for e in SPECIALISTS:
        hay = " ".join([
            e["name"],
            e["properties"]["specialty"],
            e["blurb"],
            *[t["name"] for t in e["tags"]],
        ]).lower()
        hits = sum(1 for tok in q.split() if len(tok) > 2 and tok in hay)
        if not q or hits:
            boost = 0.0
            if city and e["properties"]["city"].lower() == city.lower():
                boost = 0.5
            scored.append((hits + boost + e["affinity"] * 0.5, e))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [dict(e, _mock=True) for _, e in scored[:take]]
