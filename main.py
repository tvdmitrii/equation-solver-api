import json

from flask import Flask, request, jsonify
from Grammar import *
from CalculationFlow import *

app = Flask(__name__)


@app.route('/api/solution_request', methods=['POST'])
def solution_request():
    solution_req_data = json.loads(request.data)

    input_string = solution_req_data['equationsControl']
    guess_values = solution_req_data['guessValuesForm']
    settingsForm = solution_req_data['settingsForm']
    solution = {}

    guess_values = dict(zip(guess_values.keys(), [float(val) for val in guess_values.values()]))

    settings = {}
    settings["rads"] = int(0 if settingsForm["Trigonometry Mode"] == 'Radians' else 1)
    settings["xtol"] = float(settingsForm["Tolerance"])
    settings["iter"] = int(settingsForm["Max Iterations"])
    settings["fd_step"] = float(settingsForm["Finite Difference Step"])
    settings["decimal"] = int(settingsForm["Rounding Places"])

    CF = CalculationFlow()
    try:
        input_string = collapse_curly_brackets(input_string.splitlines())
        grammar = Grammar()

        lines_to_remove = []
        for i, line in enumerate(input_string):
            try:
                grammar.grammar.parseString(line, parseAll=True)
                lines_to_remove.append(i)
            except ParseException as err:
                continue

        for i in sorted(lines_to_remove, reverse=True):
            del input_string[i]

        grammar.update_grammar()
        try:
            grammar.parseFunctionContents(settings, guess_values)
        except ParseException as err:
            CF.success = False
            CF.error = "Parsing error at (char " + str(err.args[1]) + ") in line: " + err.markInputline("_") + "\n"
            raise err

        for line in input_string:
            try:
                result = grammar.grammar.parseString(line, parseAll=True)
            except ParseException as err:
                CF.success = False
                CF.error = "Parsing error at (char " + str(err.args[1]) + ") in line: " + err.markInputline("_") + "\n"
                raise err

        all_variable_names = sorted(set(flatten(grammar.varStack)))
        guess_values_real = dict(zip(all_variable_names, np.ones(len(all_variable_names), dtype=float)))
        dicts_update_existing(guess_values_real, guess_values)
        guess_values = guess_values_real

        CF.initialize(grammar.meta, grammar.exprStack, settings, guess_values)
        CF.solve()

        success = CF.success
        solution = dict(zip(sorted(CF.known_variables.keys()),
                            [np.round(val, int(settings["decimal"])) for val in CF.known_variables.values()]))
        error = ""
        dicts_update_existing(guess_values, solution)

    except (SolutionException, ParseException) as err:
        success = CF.success
        error = CF.error
    except Exception as err:
        success = False
        error = str(err)

    return jsonify({"success": success, "error": error, "solution": solution, "guess_values": guess_values})


app.run()
