import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Medical keywords our app recognizes
SYMPTOMS = [
    "pain", "fever", "cough", "fatigue", "nausea", "vomiting",
    "headache", "dizziness", "shortness of breath", "chest pain",
    "back pain", "sore throat", "runny nose", "chills", "sweating",
    "weakness", "swelling", "rash", "itching", "diarrhea",
    "constipation", "loss of appetite", "weight loss", "insomnia"
]

MEDICATIONS = [
    "aspirin", "ibuprofen", "paracetamol", "amoxicillin", "metformin",
    "lisinopril", "atorvastatin", "omeprazole", "levothyroxine",
    "amlodipine", "metoprolol", "hydrochlorothiazide", "sertraline",
    "albuterol", "prednisone", "insulin", "warfarin", "clopidogrel",
    "gabapentin", "pantoprazole", "acetaminophen", "penicillin"
]

DIAGNOSES = [
    "diabetes", "diabetic", "hypertension", "hypertensive", "asthma", "asthmatic",
    "pneumonia", "bronchitis", "arthritis", "arthritic",
    "depression", "depressive", "anxiety", "anxious", "migraine",
    "anemia", "anemic", "hypothyroidism", "hyperthyroidism",
    "GERD", "UTI", "influenza", "COVID", "heart failure", "kidney disease",
    "stroke", "cancer"
]

# Add this mapping to normalize variations to standard names
DIAGNOSIS_NORMALIZE = {
    "diabetic": "diabetes",
    "hypertensive": "hypertension",
    "asthmatic": "asthma",
    "arthritic": "arthritis",
    "depressive": "depression",
    "anxious": "anxiety",
    "anemic": "anemia",
}

# ICD-10 billing codes for common diagnoses
ICD10_CODES = {
    "diabetes": ("E11", "Type 2 Diabetes Mellitus"),
    "hypertension": ("I10", "Essential Hypertension"),
    "asthma": ("J45", "Asthma"),
    "pneumonia": ("J18", "Pneumonia"),
    "bronchitis": ("J40", "Bronchitis"),
    "arthritis": ("M19", "Arthritis"),
    "depression": ("F32", "Depressive Episode"),
    "anxiety": ("F41", "Anxiety Disorder"),
    "migraine": ("G43", "Migraine"),
    "anemia": ("D64", "Anemia"),
    "hypothyroidism": ("E03", "Hypothyroidism"),
    "GERD": ("K21", "GERD"),
    "UTI": ("N39", "Urinary Tract Infection"),
    "influenza": ("J11", "Influenza"),
    "COVID": ("U07", "COVID-19"),
    "heart failure": ("I50", "Heart Failure"),
    "stroke": ("I63", "Cerebral Infarction"),
}


def extract_entities(text):
    """Extract symptoms, medications, diagnoses from clinical text."""
    text_lower = text.lower()
    doc = nlp(text)

    found_symptoms = []
    found_medications = []
    found_diagnoses = []
    found_numbers = []

    # Find symptoms
    for symptom in SYMPTOMS:
        if symptom in text_lower:
            found_symptoms.append(symptom)

    # Find medications
    for med in MEDICATIONS:
        if med in text_lower:
            found_medications.append(med)

   # Find diagnoses (handle variations like diabetic→diabetes)
    for diagnosis in DIAGNOSES:
        if diagnosis.lower() in text_lower:
            normalized = DIAGNOSIS_NORMALIZE.get(diagnosis.lower(), diagnosis)
            if normalized not in found_diagnoses:
                found_diagnoses.append(normalized)

    # Find numbers (dosages, measurements like "120/80", "98.6°F")
    number_pattern = re.findall(
        r'\b\d+\.?\d*\s*(?:mg|ml|mcg|units?|°?[FC]|bpm|mmHg|kg|lbs?|%)\b'
        r'|\b\d{2,3}\/\d{2,3}\b',
        text, re.IGNORECASE
    )
    found_numbers = list(set(number_pattern))

    # Find named entities using spaCy (dates, people, organizations)
    named_entities = []
    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME", "CARDINAL", "PERSON", "ORG"]:
            named_entities.append({"text": ent.text, "type": ent.label_})

    return {
        "symptoms": list(set(found_symptoms)),
        "medications": list(set(found_medications)),
        "diagnoses": list(set(found_diagnoses)),
        "measurements": found_numbers,
        "named_entities": named_entities
    }


def get_icd10_codes(diagnoses):
    """Get ICD-10 billing codes for found diagnoses."""
    codes = []
    for diagnosis in diagnoses:
        key = diagnosis.lower()
        if key in ICD10_CODES:
            code, description = ICD10_CODES[key]
            codes.append({
                "diagnosis": diagnosis,
                "code": code,
                "description": description
            })
    return codes


def generate_soap_note(text, entities):
    """Generate a structured SOAP note from extracted entities."""
    symptoms = entities.get("symptoms", [])
    medications = entities.get("medications", [])
    diagnoses = entities.get("diagnoses", [])
    measurements = entities.get("measurements", [])

    # Build SOAP sections
    subjective = "Patient reports "
    if symptoms:
        subjective += ", ".join(symptoms) + "."
    else:
        subjective += "no specific symptoms documented."

    objective = "Vital signs and measurements: "
    if measurements:
        objective += ", ".join(measurements) + "."
    else:
        objective += "Not recorded in this note."

    assessment = "Assessment: "
    if diagnoses:
        assessment += "Patient presents with " + ", ".join(diagnoses) + "."
    else:
        assessment += "Diagnosis to be determined pending further evaluation."

    plan = "Plan: "
    if medications:
        plan += "Prescribe/continue " + ", ".join(medications) + ". "
    plan += "Follow-up as needed. Monitor symptoms and adjust treatment accordingly."

    return {
        "subjective": subjective,
        "objective": objective,
        "assessment": assessment,
        "plan": plan
    }


# Test it!
if __name__ == "__main__":
    sample = """
    Patient is a 45-year-old male presenting with chest pain and shortness
    of breath for the past 3 days. He also reports fatigue and dizziness.
    Blood pressure is 140/90 mmHg. Temperature 98.6°F. Heart rate 95 bpm.
    Patient has a history of hypertension and diabetes.
    Currently taking metformin 500mg and lisinopril 10mg.
    """

    print("Input text:")
    print(sample)
    print("\n--- Extracted Entities ---")
    entities = extract_entities(sample)
    for key, val in entities.items():
        print(f"{key}: {val}")

    print("\n--- ICD-10 Codes ---")
    codes = get_icd10_codes(entities["diagnoses"])
    for c in codes:
        print(f"{c['diagnosis']} → {c['code']} ({c['description']})")

    print("\n--- SOAP Note ---")
    soap = generate_soap_note(sample, entities)
    for section, content in soap.items():
        print(f"\n{section.upper()}:")
        print(content)