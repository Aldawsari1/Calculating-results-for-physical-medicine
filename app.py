from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from urllib.parse import quote as url_quote

app = Flask(__name__)
CORS(app)

ERROR_THRESHOLD = 2.0  # mm

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/download')
def download_file():
    return send_file('static/files/file.txt', as_attachment=True)

def check_scout_prescription(marker_position, slice_position, missalignment):
    return "Pass" if abs(missalignment) <= ERROR_THRESHOLD else "Fail"

def check_alignment_light(missalignment):
    return "Pass" if abs(missalignment) <= ERROR_THRESHOLD else "Fail"

def check_table_travel_accuracy(deviation_after_table_travel):
    deviation_limit = 2
    return "Pass" if abs(deviation_after_table_travel) <= deviation_limit else "Fail"

def verify_ct_number_accuracy(material, ct_value):
    reference_ranges = {
        "Polyethylene": (-107, -84),
        "Water": (-7, 7),
        "Air": (-1005, -970),
        "Teflon (bone)": (850, 970),
        "Acrylic": (110, 135),
    }
    return "Pass" if reference_ranges.get(material, (float('-inf'), float('inf')))[0] <= ct_value <= reference_ranges.get(material, (float('-inf'), float('inf')))[1] else "Fail"

def verify_low_contrast(cnr, svd):
    return {
        "CNR": "Pass" if cnr >= 0.4 else "Fail",
        "SVD": "Pass" if svd >= 4 else "Fail"
    }

def verify_high_contrast(spatial_resolution, threshold):
    return "Pass" if spatial_resolution >= threshold else "Fail"

def ct_number_uniformity(diff_from_center):
    return "Pass" if abs(diff_from_center) <= 5 else "Fail"

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    print("Received data:", data)
    
    test_type = data.get("test_type")
    result = "Invalid test type"
    
    if test_type == "scout_prescription":
        result = check_scout_prescription(
            data.get("marker_position", 0),
            data.get("slice_position", 0),
            data.get("missalignment", 0)
        )
    elif test_type == "alignment_light":
        result = check_alignment_light(data.get("missalignment", 0))
    elif test_type == "table_travel":
        result = check_table_travel_accuracy(data.get("deviation_after_table_travel", 0))
    elif test_type == "ct_number":
        result = verify_ct_number_accuracy(data.get("material", ""), data.get("ct_value", 0))
    elif test_type == "low_contrast":
        result = verify_low_contrast(data.get("cnr", 0), data.get("svd", 0))
    elif test_type == "high_contrast":
        result = verify_high_contrast(data.get("spatial_resolution", 0), data.get("threshold", 0))
    elif test_type == "ct_uniformity":
        result = ct_number_uniformity(data.get("diff_from_center", 0))
    else:
        return jsonify({"error": "Invalid test type"}), 400

    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
if __name__ == '__main__':
    app.run(debug=True)