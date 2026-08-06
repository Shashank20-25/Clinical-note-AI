from flask import Flask, render_template, jsonify, request
from src.extractor import extract_entities, get_icd10_codes, generate_soap_note

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400

    # Run all three steps
    entities = extract_entities(text)
    icd10 = get_icd10_codes(entities['diagnoses'])
    soap = generate_soap_note(text, entities)

    return jsonify({
        'entities': entities,
        'icd10_codes': icd10,
        'soap_note': soap
    })

if __name__ == '__main__':
    print("🏥 Clinical Note AI starting...")
    app.run(debug=True)