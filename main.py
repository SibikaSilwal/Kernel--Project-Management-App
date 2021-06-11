from Website import create_app

app = create_app()

if __name__ == '__main__': #this line makes sure that the main.py file only runs when we want to run it, and not just when we import it to some other file
    app.run(debug=True) #debug = true meaning, anytime we make change to the code and save it, it is reflected in the webserver
    