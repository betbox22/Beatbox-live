@app.route('/')
def home():
    return send_from_directory('.', 'index.html')  # אם index.html נמצא בתיקייה הראשית
    # או
    # return send_from_directory('static', 'index.html')  # אם index.html נמצא בתיקיית static
