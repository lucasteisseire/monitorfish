import pandas as pd
import plotly.express as px


def dataframe_inventory(df: pd.DataFrame, table_name=None, fig_height=None):
    fig = px.bar(
        pd.DataFrame(
            {"Valeurs renseignées": df.count(), "Valeurs distinctes": df.nunique()}
        ),
        orientation="h",
        barmode="group",
        labels={"index": "colonne", "value": "Nombre d'entrées"},
        title=f"Inventaire des données dans la table {table_name}",
    )
    if fig_height:
        fig.update_layout(height=fig_height)
    return fig


def compare_2_columns_values(df: pd.DataFrame, col_name_1: str, col_name_2: str):
    plot_df = (
        df[[col_name_1, col_name_2]]
        .dropna()
        .assign(is_equal=(lambda x: x[col_name_1] == x[col_name_2]))
        .groupby("is_equal")[[col_name_1]]
        .count()
        .T
    )

    plot_df = plot_df.rename(
        columns={True: "Valeurs identiques", False: "Valeurs différentes"}
    )

    fig = px.bar(
        plot_df,
        orientation="h",
        labels={
            "index": "",
            "value": f"Nombre d'entrées pour lesquelles {col_name_1} et {col_name_2} sont renseignées",
            "is_equal": "",
        },
        color_discrete_sequence=["blue", "green"],
    )

    fig.update_layout(
        height=200,
        width=900,
        title=f"Cohérence des données {col_name_1} et {col_name_2}",
    )
    return fig


def compare_2_columns_availability(df: pd.DataFrame, col_name_1: str, col_name_2: str):

    fig, ax = plt.subplots(figsize=(12, 7))

    all_ = set(df.index)
    set_1 = set(df[~df[col_name_1].isna()].index)
    set_2 = set(df[~df[col_name_2].isna()].index)

    fig = venn3(
        [all_, set_1, set_2], set_labels=["Ensemble", col_name_1, col_name_2], ax=ax
    )

    ax.set_title(
        f"Complétude des données {col_name_1} et {col_name_2}",
        weight="bold",
        fontsize=16,
    )

    return fig