from rasa.nlu.model import Metadata, Interpreter
import json

def pprint(o):
    print(json.dumps(o, indent=2))

interpreter = Interpreter.load('./models/nlu')

def test(sentence):
    pprint(interpreter.parse(sentence))