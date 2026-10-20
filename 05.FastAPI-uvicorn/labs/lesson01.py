from fastapi import FastAPI

app= FastAPI(title='Lsson 01')

@app.get('/')
def root():
    return {'message':'Hello FastAPI'}

@app.get('/sports')
def sports():
    return {'sport': ['Soccer','Basketball','Tennis','Baseball']}

@app.get('/menus')
def menus():
    return {'menus':['Home','About','Contact','Blog']}