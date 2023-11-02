from flask import Flask, render_template

app = Flask(__name__)

# Simple blockchain as a list (for demonstration purposes)
blockchain = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/patient_auth')
def patient_auth():
    return render_template('patient_auth.html')


@app.route('/physician')
def physician():
    return render_template('physician.html')

@app.route('/records')
def records():
    return render_template('records.html')


if __name__ == "__main__":
    app.run(debug=True)


