from app import app

def main() -> None:
    flask_server = app.create_app(template_folder="templates")
    flask_server.run()


if __name__ == "__main__":
    main()    