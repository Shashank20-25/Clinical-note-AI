"""
Clinical Note AI — Test Suite
Tests: unit tests, edge cases, and different patient scenarios
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.extractor import extract_entities, get_icd10_codes, generate_soap_note
import pytest


# ─────────────────────────────────────────
# PART 1 — Different Patient Cases
# ─────────────────────────────────────────

class TestDifferentPatients:

    def test_elderly_cardiac_patient(self):
        """58-year-old with heart issues."""
        text = """
        Patient is a 58-year-old male with chest pain and shortness of breath.
        Blood pressure 160/100 mmHg. Heart rate 95 bpm.
        History of heart failure and hypertension.
        Taking aspirin 81mg and lisinopril 10mg daily.
        """
        entities = extract_entities(text)
        assert "chest pain" in entities["symptoms"]
        assert "aspirin" in entities["medications"]
        assert "hypertension" in entities["diagnoses"]
        assert "heart failure" in entities["diagnoses"]
        print("✅ Elderly cardiac patient — PASSED")

    def test_diabetic_patient(self):
        """Patient with diabetes and related symptoms."""
        text = """
        Patient presents with fatigue and weakness.
        Blood sugar 280 mg/dl. Weight 95 kg.
        Known diabetic, currently on metformin 1000mg twice daily.
        Also complains of nausea and loss of appetite.
        """
        entities = extract_entities(text)
        assert "fatigue" in entities["symptoms"]
        assert "metformin" in entities["medications"]
        assert "diabetes" in entities["diagnoses"]
        print("✅ Diabetic patient — PASSED")

    def test_respiratory_patient(self):
        """Patient with breathing problems."""
        text = """
        27-year-old female with cough and shortness of breath.
        Temperature 101°F. History of asthma since childhood.
        Using albuterol inhaler as needed.
        Symptoms worsening over past week.
        """
        entities = extract_entities(text)
        assert "cough" in entities["symptoms"]
        assert "albuterol" in entities["medications"]
        assert "asthma" in entities["diagnoses"]
        print("✅ Respiratory patient — PASSED")

    def test_mental_health_patient(self):
        """Patient with mental health conditions."""
        text = """
        Patient reports persistent fatigue, insomnia, and loss of appetite
        for the past month. Diagnosed with depression and anxiety.
        Currently prescribed sertraline 50mg once daily.
        """
        entities = extract_entities(text)
        assert "fatigue" in entities["symptoms"]
        assert "insomnia" in entities["symptoms"]
        assert "sertraline" in entities["medications"]
        assert "depression" in entities["diagnoses"]
        assert "anxiety" in entities["diagnoses"]
        print("✅ Mental health patient — PASSED")

    def test_multiple_medications(self):
        """Patient on many medications."""
        text = """
        Patient taking metformin 500mg, aspirin 100mg,
        lisinopril 20mg, and omeprazole 20mg daily.
        """
        entities = extract_entities(text)
        assert len(entities["medications"]) >= 3
        print(f"✅ Multiple medications ({len(entities['medications'])} found) — PASSED")


# ─────────────────────────────────────────
# PART 2 — Edge Cases
# ─────────────────────────────────────────

class TestEdgeCases:

    def test_empty_input(self):
        """Empty string should return empty lists."""
        entities = extract_entities("")
        assert entities["symptoms"] == []
        assert entities["medications"] == []
        assert entities["diagnoses"] == []
        assert entities["measurements"] == []
        print("✅ Empty input — PASSED")

    def test_whitespace_only(self):
        """Only spaces and newlines."""
        entities = extract_entities("   \n\n\t   ")
        assert entities["symptoms"] == []
        assert entities["medications"] == []
        print("✅ Whitespace only — PASSED")

    def test_no_medical_content(self):
        """Random non-medical text."""
        text = "The weather today is sunny and warm. I went to the park."
        entities = extract_entities(text)
        assert entities["symptoms"] == []
        assert entities["medications"] == []
        assert entities["diagnoses"] == []
        print("✅ No medical content — PASSED")

    def test_numbers_only(self):
        """Just numbers, no medical words."""
        text = "1234 5678 9000 42 100"
        entities = extract_entities(text)
        assert entities["symptoms"] == []
        assert entities["medications"] == []
        print("✅ Numbers only — PASSED")

    def test_uppercase_input(self):
        """Text in all caps."""
        text = "PATIENT HAS DIABETES AND HYPERTENSION. TAKING METFORMIN."
        entities = extract_entities(text)
        assert "diabetes" in entities["diagnoses"]
        assert "hypertension" in entities["diagnoses"]
        assert "metformin" in entities["medications"]
        print("✅ Uppercase input — PASSED")

    def test_very_long_text(self):
        """Very long clinical note."""
        text = """
        Patient is a 65-year-old male with chest pain, shortness of breath,
        fatigue, dizziness, nausea, vomiting, headache, weakness, and swelling.
        Blood pressure 180/110 mmHg. Temperature 100.4°F. Heart rate 110 bpm.
        Weight 110 kg. Blood sugar 320 mg/dl.
        History of hypertension, diabetes, heart failure, asthma, depression,
        anxiety, and arthritis spanning the last 20 years.
        Currently on metformin 1000mg, lisinopril 40mg, aspirin 81mg,
        albuterol as needed, sertraline 100mg, omeprazole 20mg, and
        prednisone 5mg daily.
        """ * 3  # repeat 3 times to make it very long
        entities = extract_entities(text)
        assert len(entities["symptoms"]) > 0
        assert len(entities["medications"]) > 0
        assert len(entities["diagnoses"]) > 0
        print(f"✅ Very long text — PASSED ({len(text)} chars)")

    def test_unknown_icd10(self):
        """Diagnosis with no ICD-10 code mapped."""
        codes = get_icd10_codes(["rare_unknown_disease_xyz"])
        assert codes == []
        print("✅ Unknown ICD-10 diagnosis — PASSED")

    def test_empty_icd10(self):
        """Empty list of diagnoses."""
        codes = get_icd10_codes([])
        assert codes == []
        print("✅ Empty ICD-10 input — PASSED")


# ─────────────────────────────────────────
# PART 3 — Unit Tests
# ─────────────────────────────────────────

class TestUnits:

    def test_icd10_diabetes(self):
        """ICD-10 code for diabetes must be E11."""
        codes = get_icd10_codes(["diabetes"])
        assert len(codes) == 1
        assert codes[0]["code"] == "E11"
        assert codes[0]["diagnosis"] == "diabetes"
        print("✅ ICD-10 diabetes code — PASSED")

    def test_icd10_hypertension(self):
        """ICD-10 code for hypertension must be I10."""
        codes = get_icd10_codes(["hypertension"])
        assert len(codes) == 1
        assert codes[0]["code"] == "I10"
        print("✅ ICD-10 hypertension code — PASSED")

    def test_icd10_multiple(self):
        """Multiple diagnoses return multiple codes."""
        codes = get_icd10_codes(["diabetes", "hypertension", "asthma"])
        assert len(codes) == 3
        code_list = [c["code"] for c in codes]
        assert "E11" in code_list
        assert "I10" in code_list
        assert "J45" in code_list
        print("✅ Multiple ICD-10 codes — PASSED")

    def test_soap_has_all_sections(self):
        """SOAP note must always have all 4 sections."""
        text = "Patient has chest pain and diabetes. Taking aspirin."
        entities = extract_entities(text)
        soap = generate_soap_note(text, entities)
        assert "subjective" in soap
        assert "objective" in soap
        assert "assessment" in soap
        assert "plan" in soap
        print("✅ SOAP note has all 4 sections — PASSED")

    def test_soap_empty_entities(self):
        """SOAP note works even with no entities found."""
        soap = generate_soap_note("", {
            "symptoms": [],
            "medications": [],
            "diagnoses": [],
            "measurements": []
        })
        assert "subjective" in soap
        assert "objective" in soap
        assert "assessment" in soap
        assert "plan" in soap
        print("✅ SOAP note with empty entities — PASSED")

    def test_extract_returns_correct_keys(self):
        """extract_entities must always return these exact keys."""
        entities = extract_entities("some text")
        required_keys = ["symptoms", "medications", "diagnoses",
                        "measurements", "named_entities"]
        for key in required_keys:
            assert key in entities, f"Missing key: {key}"
        print("✅ extract_entities returns correct keys — PASSED")

    def test_measurements_detected(self):
        """Common medical measurements are detected."""
        text = "BP 120/80 mmHg. Temp 98.6°F. Weight 70 kg. HR 72 bpm."
        entities = extract_entities(text)
        assert len(entities["measurements"]) > 0
        print(f"✅ Measurements detected: {entities['measurements']} — PASSED")

    def test_no_duplicate_symptoms(self):
        """Same symptom mentioned twice should only appear once."""
        text = "Patient has chest pain. The chest pain has been severe."
        entities = extract_entities(text)
        assert entities["symptoms"].count("chest pain") == 1
        print("✅ No duplicate symptoms — PASSED")


# ─────────────────────────────────────────
# Run all tests with summary
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*55)
    print("   CLINICAL NOTE AI — FULL TEST SUITE")
    print("="*55)

    print("\n📋 PART 1: Different Patient Cases")
    print("-"*40)
    p = TestDifferentPatients()
    p.test_elderly_cardiac_patient()
    p.test_diabetic_patient()
    p.test_respiratory_patient()
    p.test_mental_health_patient()
    p.test_multiple_medications()

    print("\n⚠️  PART 2: Edge Cases")
    print("-"*40)
    e = TestEdgeCases()
    e.test_empty_input()
    e.test_whitespace_only()
    e.test_no_medical_content()
    e.test_numbers_only()
    e.test_uppercase_input()
    e.test_very_long_text()
    e.test_unknown_icd10()
    e.test_empty_icd10()

    print("\n🔬 PART 3: Unit Tests")
    print("-"*40)
    u = TestUnits()
    u.test_icd10_diabetes()
    u.test_icd10_hypertension()
    u.test_icd10_multiple()
    u.test_soap_has_all_sections()
    u.test_soap_empty_entities()
    u.test_extract_returns_correct_keys()
    u.test_measurements_detected()
    u.test_no_duplicate_symptoms()

    print("\n" + "="*55)
    print("   ALL TESTS COMPLETED!")
    print("="*55)