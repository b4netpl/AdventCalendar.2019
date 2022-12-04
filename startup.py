from advencal import create_app, init_db_cli

app = create_app()
init_db_cli.register(app)

if __name__ == "__main__":
    app.run()
