"""
Streamlit App for Stroke Risk Prediction

Production-ready web interface for the stroke prediction model.
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.inference import predict, validate_input, load_model_artifacts

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Stroke Risk Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Load model on startup
# ---------------------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load model artifacts (cached)."""
    load_model_artifacts()
    return True

load_model()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966331.png", width=100)
    st.title("🧠 Stroke Risk Predictor")
    st.markdown("---")
    st.markdown("""
    **About this tool:**
    This application predicts stroke risk based on patient health data using a trained 
    XGBoost machine learning model.
    
    **Model Performance:**
    - ROC-AUC: 0.82
    - Recall: 0.27 (captures 27% of stroke cases)
    - Precision: 0.19
    
    **⚠️ Disclaimer:** This tool is for educational purposes only. 
    It does not replace professional medical advice.
    """)
    st.markdown("---")
    
    # Threshold slider
    threshold = st.slider(
        "Decision Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.05,
        help=(
            "Lower = more sensitive (catch more strokes, more false alarms). "
            "Higher = more specific."
        ),
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("Stroke Risk Assessment")
st.markdown("Enter patient information to assess stroke risk.")

# Input form
with st.form("patient_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Demographics")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=0, max_value=120, value=50)
        ever_married = st.selectbox("Ever Married", ["Yes", "No"])
        work_type = st.selectbox(
            "Work Type",
            ["Private", "Self-employed", "Govt_job", "children", "Never_worked"]
        )
        residence_type = st.selectbox("Residence Type", ["Urban", "Rural"])
    
    with col2:
        st.subheader("Health Metrics")
        hypertension = st.selectbox(
            "Hypertension", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No"
        )
        heart_disease = st.selectbox(
            "Heart Disease", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No"
        )
        avg_glucose_level = st.number_input(
            "Avg Glucose Level (mg/dL)", min_value=0.0, max_value=400.0, value=100.0, step=1.0
        )
        bmi = st.number_input("BMI", min_value=0.0, max_value=60.0, value=25.0, step=0.1)
        smoking_status = st.selectbox(
            "Smoking Status", ["never smoked", "formerly smoked", "smokes", "Unknown"]
        )
    
    submitted = st.form_submit_button(
        "🔍 Predict Stroke Risk", type="primary", use_container_width=True
    )

# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------
if submitted:
    patient_data = {
        "gender": gender,
        "age": age,
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "ever_married": ever_married,
        "work_type": work_type,
        "Residence_type": residence_type,
        "avg_glucose_level": avg_glucose_level,
        "bmi": bmi,
        "smoking_status": smoking_status,
    }
    
    # Validate
    valid, msg = validate_input(patient_data)
    if not valid:
        st.error(f"Invalid input: {msg}")
    else:
        # Temporarily override threshold
        import ml.inference as inference_module
        original_threshold = inference_module._threshold
        inference_module._threshold = threshold
        
        try:
            result = predict(patient_data)
        finally:
            inference_module._threshold = original_threshold
        
        # Display results
        st.markdown("---")
        
        if result["stroke_risk"]:
            st.error("## ⚠️ HIGH STROKE RISK")
        else:
            st.success("## ✅ LOW STROKE RISK")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Risk Probability", f"{result['probability']:.1%}")
        with col2:
            st.metric("Decision Threshold", f"{result['threshold']:.2f}")
        with col3:
            st.metric("Risk Level", result['risk_level'])
        
        # Progress bar for probability
        st.progress(result['probability'])
        
        # Interpretation
        st.markdown("### Interpretation")
        if result["stroke_risk"]:
            st.warning("""
            **This patient shows elevated risk factors for stroke.**
            
            **Recommended actions:**
            - Consult a healthcare provider for comprehensive evaluation
            - Monitor blood pressure regularly
            - Manage glucose levels
            - Consider lifestyle modifications (diet, exercise, smoking cessation)
            - Discuss preventive medications with doctor
            """)
        else:
            st.info("""
            **This patient does not show elevated stroke risk based on the provided factors.**
            
            **Recommended actions:**
            - Maintain healthy lifestyle (balanced diet, regular exercise)
            - Continue regular health check-ups
            - Monitor blood pressure and glucose periodically
            - Avoid smoking
            """)
        
        # Feature importance (from trained model)
        st.markdown("---")
        st.markdown("### Key Risk Factors (Model Feature Importance)")
        
        try:
            import joblib
            model = joblib.load("backend/ml/artifacts/model.joblib")
            feature_names = ["age", "hypertension", "heart_disease", "ever_married", 
                           "work_type", "Residence_type", "avg_glucose_level", "bmi", 
                           "gender", "smoking_status"]
            importance = model.feature_importances_
            
            import pandas as pd
            fi_df = pd.DataFrame({"Feature": feature_names, "Importance": importance})
            fi_df = fi_df.sort_values("Importance", ascending=True)
            
            st.bar_chart(fi_df.set_index("Feature"))
        except Exception:
            pass
        
        # Raw JSON output
        with st.expander("View Raw Prediction Data"):
            st.json(result)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Stroke Risk Predictor v1.0 | Built with Streamlit & XGBoost</p>
    <p>For educational purposes only - Not a medical device</p>
</div>
""", unsafe_allow_html=True)