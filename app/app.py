"""..."""
from flask import Flask, render_template

from app.db_utils import crud, models


def create_app(template_folder: str = "templates") -> Flask:
    """..."""
    app = Flask(__name__, template_folder=template_folder)

    @app.route("/")
    def home():
        return render_template("index.html")


    # @app.route('/submit', methods=['POST'])
    # def submit():
    #     field1 = request.form.get('field1', '')
    #     return 'Data submitted successfully!'

        crud.insert(models.TaskTable, models.Task)



    return app
