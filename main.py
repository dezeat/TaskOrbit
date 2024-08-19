from flask import Flask, request, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return render_template("index.html")

    @app.route('/submit', methods=['POST'])
    def submit():
        field1 = request.form.get('field1', '')

        return 'Data submitted successfully!'

    return app