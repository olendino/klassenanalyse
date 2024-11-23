import streamlit as st

col1, col2 = st.columns([1,1])

st.header("Klassenanalyse")
#st.write("Die Klassenanalyse die auf dieser Website dargestellt wird basiert auf der Arbeit von D.W:. Liviingstone zentrale Modell seiner Klassanalyse, welches er aus dem Zensus generiert kann lässt sich mit dieser einfachen Graphik:")
st.markdown("## Livingstone")

with col2.expander("Willst du mehr wissen?"):
    st.write("Die Klassenanalyse die auf dieser Website dargestellt wird basiert auf der Arbeit von D.W:. Liviingstone zentrale Modell seiner Klassanalyse, welches er aus dem Zensus generiert kann lässt sich mit dieser einfachen Graphik:")



st.image("/Users/leonardhaas/code/streamlit/class_canada_2016.png", caption="Livingstone class model")
