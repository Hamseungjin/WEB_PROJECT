from flask import jsonify, render_template, Flask,request

from chat import get_response

app=Flask(__name__)

@app.get("/")
def index_get():
    return render_template("base.html")

@app.post("/predict")
def predict():
    text=request.get_json().get("message")
    # TODO : check if text is vaild
    response = get_response(text)
    message={"answer":response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)