from app_init import create_app

app = create_app()

if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/brands/add")
    app.run(debug=True)
