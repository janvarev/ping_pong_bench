import os
import fire  # type: ignore
import json
from typing import Optional
from pathlib import Path
from statistics import mean

import pandas as pd  # type: ignore
from tabulate import tabulate


def build_table(results_dir: str, output_path: Optional[str] = None) -> None:
    records = []
    for file_name in os.listdir(results_dir):
        file_path = Path(os.path.join(results_dir, file_name))
        model_name = file_path.stem
        with open(file_path, encoding="utf-8") as r:
            result = json.load(r)
        outputs = result.pop("outputs")
        result["num_situations"] = len(outputs)
        result["avg_length"] = int(mean([len(m["content"]) for o in outputs for m in o["messages"] if m["role"] == "assistant"]))
        result["model_name"] = model_name
        records.append(result)
    columns = [
        "model_name",
        "final_score",
        "refusal_ratio",
        "stay_in_character_score",
        "language_fluency_score",
        "entertainment_score",
        "num_situations",
        "avg_length"
    ]
    pd.set_option("display.precision", 2)

    # Set display options to show all columns
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    df = pd.DataFrame(records).sort_values(by="final_score", ascending=False)[columns]
    print(df)

    # Convert DataFrame to list of lists for tabulate
    table_data = df.values.tolist()

    # Add column names as the first row
    columns = [row.replace("_", " ").capitalize() for row in columns]
    table_data.insert(0, columns)

    # Create the table using tabulate
    table = tabulate(table_data, headers="firstrow", tablefmt="github", floatfmt=".2f")

    # Output table in Github MD format
    # print("\n----- Github MD format -----\n")
    # print(table)

    if output_path:
        table = "# Results\n\n" + table
        with open(output_path, "w") as w:
            w.write(table)


if __name__ == "__main__":
    fire.Fire(build_table)
