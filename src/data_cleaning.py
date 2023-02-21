import pandas as pd


def location_processing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the "location" feature of the dataframe by using two mapping tables

    city_long_lat: mapping table to link city to its longitude & latitude
    price_index_state_2020: mapping table to link state to its 2022 price index

    state: job offer state if provided else nan
    city: job offer city
    latitude: city's latitude
    longitude: city's longitude
    price_index: state's 2022 price index

    returns: pd.DataFrame.
    """
    city_long_lat = pd.read_excel("data/city_long_lat.xlsx").set_index("city")
    price_index_state = pd.read_excel("data/price_index_state_2022.xlsx").set_index(
        "state_id"
    )

    df["location"] = df.location.astype("str")
    df["state"] = df.location.apply(
        lambda x: x.split(",")[-1].strip() if len(x.split(",")) > 1 else "nan"
    )
    df["city"] = df.location.apply(lambda x: x.split(",")[0].strip())
    df["latitude"] = df.city.apply(
        lambda x: city_long_lat.loc[x, "lat"] if x in city_long_lat.index else "nan"
    )
    df["longitude"] = df.city.apply(
        lambda x: city_long_lat.loc[x, "lng"] if x in city_long_lat.index else "nan"
    )
    df["price_index"] = df.state.apply(
        lambda x: price_index_state.loc[x, "index"] * 0.01  # type: ignore
        if x in price_index_state.index
        else 1
    )

    print("location processed")
    return df


def salary_processing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the 'salary_estimate' feature of the dataframe

    employer_provided_salary: 1 if the salary is provided by employee, else 0
    salary_per_hour: 1 if the provided salary is per hour, else 0
    currency: $, € or £
    low_salary: lower bound of the displayed salary
    high_salary: upper bound of the displayed salary
    optimist_salary: weighted mean of low_salary & high salary, giving more importance
    to high_salary because I believe that it is the most up-to-date & relevant for my position
    purchasing_power: optimist_salary / state_price_index

    returns pd.DataFrame.
    """
    df["salary_estimate"] = df.salary_estimate.astype("str")

    df["employer_provided_salary"] = df.salary_estimate.apply(
        lambda x: 1 if "Employer Provided" in x else 0
    )
    df["salary_per_hour"] = df.salary_estimate.apply(
        lambda x: 1 if "Per Hour" in x else 0
    )
    df["salary_estimate"] = df.salary_estimate.apply(
        lambda x: x.strip()
        .split(":")[-1]
        .split("(")[0]  # erase "employer provided salary"
        .split("P")[0]  # erase "glassdoor estimate"
        .replace("K", "000")  # erase "per hour"
    )
    df["currency"] = df.salary_estimate.apply(
        lambda x: "$" if "$" in x else "£" if "£" in x else "€" if "€" in x else "nan"
    )
    df["low_salary"] = df.salary_estimate.apply(
        lambda x: x.split("-")[0].replace("$", "")
    )
    df["high_salary"] = df.salary_estimate.apply(
        lambda x: x.split("-")[-1].replace("$", "")
    )

    df["optimist_salary"] = (
        df.high_salary.astype(float) * 4 + df.low_salary.astype(float)
    ) / 5

    filter = df.salary_per_hour == 1

    df.loc[filter, "optimist_salary"] = df.loc[filter, "optimist_salary"] * 2080

    df["purchasing_power"] = df.optimist_salary / df.price_index

    print("salaries processed")
    return df


def company_name_processing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the 'company_name' feature of the dataframe

    rating: company rating if provided else nan

    returns: pd.DataFrame.
    """
    df["company_name"] = df.company_name.astype("str")
    df["rating"] = df.company_name.apply(
        lambda x: x.split("\n")[-1] if len(x.split("\n")) > 1 else "nan"
    )
    df["company_name"] = df.company_name.apply(lambda x: x.split("\n")[0])
    return df


def data_cleaning_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data cleaning pipeline using all the above functions

    returns: pd.DataFrame.
    """
    df = df.drop_duplicates()
    df = df[~df.salary_estimate.isna()]
    df = company_name_processing(df)
    df = location_processing(df)
    df = salary_processing(df)
    print("output cleaned")
    return df
