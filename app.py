import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Healthcare Cloud Cost Intelligence Dashboard")

# ---------------- UPLOAD ----------------
uploaded_file = st.file_uploader("Upload your Cloud Billing CSV", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)
    st.success("Dataset loaded successfully")

    # ---------------- VALIDATION ----------------
    required_cols = ['service_type', 'cost', 'month']

    if not all(col in df.columns for col in required_cols):
        st.error("Dataset must contain service_type, cost, and month columns")
        st.stop()

    # ---------------- DATA PREVIEW ----------------
    st.subheader("Dataset Preview")
    st.write(df.head())

    # ---------------- FIX TYPES ----------------
    if 'seasonal_effect' in df.columns:
        df['seasonal_effect'] = df['seasonal_effect'].astype(bool)

    # Ensure month sorting
    month_order = list(range(1, 13))
    monthly_cost = df.groupby('month')['cost'].sum().reindex(month_order)

    # ---------------- KPI METRICS ----------------
    st.subheader("Key Metrics")

    total_cost = df['cost'].sum()
    avg_cost = df['cost'].mean()
    peak_month_cost = monthly_cost.max()

    threshold = df['cost'].mean() + 2 * df['cost'].std()
    anomaly_count = df[df['cost'] > threshold].shape[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cost", f"$ {total_cost:,.0f}")
    col2.metric("Average Cost", f"$ {avg_cost:,.2f}")
    col3.metric("Peak Month Cost", f"$ {peak_month_cost:,.0f}")
    col4.metric("Anomalies", anomaly_count)

    # ---------------- SERVICE COST ----------------
    st.subheader("Cost Distribution by Service")

    service_cost = df.groupby('service_type')['cost'].sum()

    fig1, ax1 = plt.subplots()
    service_cost.plot(kind='pie', autopct='%1.1f%%', ax=ax1)
    ax1.set_ylabel("")
    st.pyplot(fig1)

    # ---------------- DEPARTMENT COST ----------------
    st.subheader("Cost Distribution by Department")

    if 'department' in df.columns:
        dept_cost = df.groupby('department')['cost'].sum().sort_values(ascending=False)

        fig_dept, ax_dept = plt.subplots()
        dept_cost.plot(kind='bar', ax=ax_dept)

        ax_dept.set_ylabel("Total Cost")
        ax_dept.set_title("Cost by Department")

        st.pyplot(fig_dept)
    else:
        st.warning("Department column not available")

    # ---------------- MONTHLY TREND ----------------
    st.subheader("Monthly Cost Trend")

    fig_month, ax_month = plt.subplots()
    ax_month.plot(monthly_cost.index, monthly_cost.values, marker='o')

    ax_month.set_xlabel("Month")
    ax_month.set_ylabel("Total Cost")
    ax_month.set_title("Monthly Cost Trend")

    st.pyplot(fig_month)

    # ---------------- SEASONAL ANALYSIS ----------------
    st.subheader("Seasonal Impact on Cost")

    if 'seasonal_effect' in df.columns:

        seasonal_cost = df.groupby('seasonal_effect')['cost'].mean()
        seasonal_cost.index = ['Non-Seasonal', 'Seasonal']

        fig_season, ax_season = plt.subplots()
        colors = ['blue', 'orange']

        ax_season.bar(seasonal_cost.index, seasonal_cost.values, color=colors)
        ax_season.set_ylabel("Average Cost")
        ax_season.set_title("Seasonal vs Non-Seasonal Cost")

        st.pyplot(fig_season)

    else:
        st.warning("Seasonal data not available")

    # ---------------- ANOMALY DETECTION ----------------
    st.subheader("Anomaly Detection (Rule-based)")

    df['Anomaly'] = df['cost'].apply(
        lambda x: 'Anomaly' if x > threshold else 'Normal'
    )

    fig3, ax3 = plt.subplots()

    colors = df['Anomaly'].map({
        'Normal': 'blue',
        'Anomaly': 'red'
    })

    ax3.scatter(range(len(df)), df['cost'], c=colors)
    ax3.axhline(threshold, linestyle='--')

    ax3.set_xlabel("Data Points")
    ax3.set_ylabel("Cost")
    ax3.set_title("Anomaly Detection")

    st.pyplot(fig3)

    st.write("Number of anomalies detected:", anomaly_count)

    # ---------------- COST COMPONENT BREAKDOWN ----------------
    st.subheader("Cost Component Breakdown")

    components = ['compute_cost', 'storage_cost', 'transfer_cost', 'api_cost']
    available = [c for c in components if c in df.columns]

    if available:
        comp_sum = df[available].sum()

        fig4, ax4 = plt.subplots()
        comp_sum.plot(kind='pie', autopct='%1.1f%%', ax=ax4)
        ax4.set_ylabel("")

        st.pyplot(fig4)
    else:
        st.warning("Cost component columns not available")

    # ---------------- AUTO INSIGHTS ----------------
    st.subheader("Auto-Generated Insights")

    insights = []

    highest_service = service_cost.idxmax()
    lowest_service = service_cost.idxmin()

    insights.append(f"Highest cost is contributed by '{highest_service}'.")
    insights.append(f"Lowest cost is from '{lowest_service}'.")

    peak_month = monthly_cost.idxmax()
    low_month = monthly_cost.idxmin()

    insights.append(f"Peak cost observed in month {peak_month}.")
    insights.append(f"Lowest cost observed in month {low_month}.")

    if 'seasonal_effect' in df.columns:
        seasonal_cost = df.groupby('seasonal_effect')['cost'].mean()

        if True in seasonal_cost and False in seasonal_cost:
            if seasonal_cost[True] > seasonal_cost[False]:
                diff = ((seasonal_cost[True] - seasonal_cost[False]) / seasonal_cost[False]) * 100
                insights.append(f"Seasonal periods show approximately {diff:.1f}% higher cost.")

    if anomaly_count > 0:
        insights.append(f"{anomaly_count} anomalies detected indicating unusual cost spikes.")

    if available:
        top_component = comp_sum.idxmax()
        insights.append(f"'{top_component}' is the major contributor to total cost.")

    for ins in insights:
        st.write("•", ins)

    # ---------------- SMART RECOMMENDATIONS ----------------
    st.subheader("Smart Recommendations")

    st.write(f"• Optimize usage of '{highest_service}' to reduce cost.")

    if anomaly_count > 0:
        st.write("• Investigate anomaly spikes to prevent unexpected billing.")

    if 'seasonal_effect' in df.columns:
        st.write("• Plan resources in advance for seasonal demand.")

    if available:
        st.write(f"• Focus on '{top_component}' to achieve maximum cost savings.")

else:
    st.warning("Please upload a CSV file to proceed")