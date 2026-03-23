from flask import Flask, render_template, request

app = Flask(__name__)

UNITS = ["Cardio", "Digestif", "Urinaire", "Endocrino", "Neuro"]
EXAM_ONLY = ["Génétique", "Immuno"]


def to_float(value):
    value = str(value).strip().replace(",", ".")
    if value == "":
        raise ValueError("هناك خانة فارغة")
    note = float(value)
    if note < 0 or note > 20:
        raise ValueError("كل نقطة يجب أن تكون بين 0 و 20")
    return note


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    form_data = {}

    if request.method == "POST":
        try:
            final_notes = {}
            rattrapage = []
            weighted_sum = 0
            total_coef = 0

            # الوحدات: معامل 2
            for unit in UNITS:
                tp_key = f"{unit}_tp"
                ex_key = f"{unit}_ex"

                form_data[tp_key] = request.form.get(tp_key, "")
                form_data[ex_key] = request.form.get(ex_key, "")

                tp = to_float(form_data[tp_key])
                ex = to_float(form_data[ex_key])

                moyenne = (tp + (4 * ex)) / 5
                moyenne = round(moyenne, 2)

                final_notes[unit] = moyenne

                if moyenne < 5:
                    rattrapage.append(unit)

                weighted_sum += moyenne * 2
                total_coef += 2

            # المقاييس: معامل 1
            for subject in EXAM_ONLY:
                ex_key = f"{subject}_ex"
                form_data[ex_key] = request.form.get(ex_key, "")

                ex = to_float(form_data[ex_key])
                ex = round(ex, 2)

                final_notes[subject] = ex

                if ex < 5:
                    rattrapage.append(subject)

                weighted_sum += ex * 1
                total_coef += 1

            general_average = round(weighted_sum / total_coef, 2)
            status = "ناجح" if general_average >= 10 else "راسب - امتحان استدراك"

            results = {
                "final_notes": final_notes,
                "rattrapage": rattrapage,
                "general_average": general_average,
                "status": status
            }

        except ValueError as e:
            error = str(e)
        except Exception:
            error = "حدث خطأ أثناء الحساب"

    return render_template(
        "index.html",
        units=UNITS,
        exam_only=EXAM_ONLY,
        results=results,
        error=error,
        form_data=form_data
    )


if __name__ == "__main__":
    app.run(debug=True)
