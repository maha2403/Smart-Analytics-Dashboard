
from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder="pages",
    static_folder="assets"
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("welcome.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    total_records = 0
    total_columns = 0
    numeric_count = 0
    columns = []
    rows = []
    chart_data = None
    error = None

    if request.method == "POST":

        file = request.files.get("dataset")

        if not file or file.filename == "":
            error = "Please select a CSV file."

        elif not file.filename.lower().endswith(".csv"):
            error = "Only CSV files are allowed."

        else:
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )

                file.save(filepath)

                df = pd.read_csv(filepath)

                total_records = len(df)
                total_columns = len(df.columns)
                columns = df.columns.tolist()

                numeric_columns = df.select_dtypes(
                    include="number"
                ).columns.tolist()

                numeric_count = len(numeric_columns)

                # Dataset preview
                rows = df.head(10).fillna("").to_dict(
                    orient="records"
                )

                # Chart data
                if numeric_columns and not df.empty:

                    selected_column = numeric_columns[0]

                    chart_values = (
                        df[selected_column]
                        .head(10)
                        .fillna(0)
                        .tolist()
                    )

                    chart_data = {
                        "labels": [
                            f"Record {i+1}"
                            for i in range(len(chart_values))
                        ],
                        "values": chart_values,
                        "column": selected_column
                    }

            except Exception as e:
                error = f"Error processing dataset: {str(e)}"

    return render_template(
        "insights.html",
        total_records=total_records,
        total_columns=total_columns,
        numeric_count=numeric_count,
        columns=columns,
        rows=rows,
        chart_data=chart_data,
        error=error,
        uploaded=chart_data is not None or total_columns > 0
    )


if __name__ == "__main__":
    app.run(debug=True)
