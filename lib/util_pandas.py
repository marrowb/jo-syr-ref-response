import pandas as pd
import textwrap


def show_full(dataframe):
    with pd.option_context("display.max_colwidth", None):
        display(dataframe)

        import textwrap


def show_text_wrapped(df, width=80):
    for idx, row in df.iterrows():
        print(f"=== Row {idx} ===")
        for col in df.columns:
            print(f"\n{col.upper()}:")
            # Wrap text to specified width
            wrapped = textwrap.fill(str(row[col]), width=width)
            print(wrapped)
        print("\n" + "=" * 50 + "\n")
