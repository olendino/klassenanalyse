import streamlit as st

st.markdown(
    """
    ## Wright transformation with R DIGCLASS
   
    Argument | Description
    x | A character vector of 4-digit ISCO-88 codes (e.g., use "1310" instead of "131").
    is_supervisor | A numeric vector where 1 indicates the individual is a supervisor, and 0 indicates they are not.
    self_employed | A numeric vector where 1 indicates the individual is self-employed, and 0 means they are an employee.
    n_employees | A numeric vector representing the number of employees managed by each individual.
    control_work | A numeric score (0–10) representing how much control the individual has over organizational decisions. 0 = no control, 10 = full control. Example variable: iorgact from the European Social Survey.
    control_daily | A numeric score (1–4) indicating control over one's daily work. 1 = complete control, 4 = no control. Example variable: orgwrk or a recoded version of wkdcorga from the European Social Survey.
    type | The classification scheme to use: "simple", "decision-making", or "power-class".
    label | Logical. If TRUE, returns the class labels instead of just the codes. Default is FALSE.
    to_factor | Logical. If TRUE, the output will be a factor. The levels follow the sorted Wright codes. Default is FALSE.
    """
)