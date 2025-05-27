import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page configuration
st.set_page_config(
    page_title="European Scaleup Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #1E3A8A;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-description {
        font-size: 0.9rem;
        color: #475569;
        margin-bottom: 1rem;
    }
    .stPlotlyChart {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .footer {
        font-size: 0.8rem;
        color: #64748B;
        text-align: center;
        margin-top: 2rem;
        border-top: 1px solid #E2E8F0;
        padding-top: 1rem;
    }
    .country-pill {
        display: inline-block;
        padding: 5px 10px;
        background-color: #E2E8F0;
        border-radius: 15px;
        margin-right: 5px;
        margin-bottom: 5px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data function with error handling
@st.cache_data
def load_data():
    try:
        return pd.read_excel('Aggregate country with country.xlsx')
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'Aggregate country with country.xlsx' is in the same directory as this app.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Main app layout
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### European Scaleup Monitor")
        st.markdown("---")
        
        # Metric definitions in expandable section
        with st.expander("📊 Metric Definitions", expanded=False):
            st.markdown("""
            - **Scaler**: Companies with average annual growth rate of 10% in past three years
            - **High Growth Firm**: Companies with average annual growth rate of 20% in past three years
            - **Consistent High Growth Firm**: High growth companies that grew 20% in at least 2 of the past three years
            - **Consistent Hypergrower**: High growth companies that grew 40% in at least 2 of the past three years
            - **Gazelle**: Consistent high growth firm that is younger than 10 years
            - **Mature High Growth Firm**: Consistent high growth firm that is older than 10 years
            - **Scaleup**: Consistent hypergrower that is younger than 10 years
            - **Superstar**: Consistent hypergrower that is older than 10 years
            """)
        
        st.markdown("---")
        st.markdown("#### About")
        st.markdown("This tool allows you to benchmark countries in Europe on different growth metrics.")
        st.markdown("[Visit Scaleup Institute](https://scaleupinstitute.eu/)")
        st.markdown("Contact: info@scaleupinstitute.eu")
        
    # Main content
    st.markdown('<div class="main-header">European Scaleup Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Benchmarking of countries in Europe</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Create two columns for filters
    col1, col2 = st.columns([2, 1])
    
    # Country selection with better UX
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        countries = sorted(df['Country'].unique())
        selected_countries = st.multiselect(
            'Select countries to compare',
            countries,
            default=countries[:3] if len(countries) >= 3 else countries[:1],
            help="Choose multiple countries to compare their performance"
        )
        
        # Show selected countries as pills
        if selected_countries:
            pills_html = "Selected: " + " ".join([f'<span class="country-pill">{country}</span>' for country in selected_countries])
            st.markdown(pills_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics selection with better UX
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        metrics_mapping = {
            'Scaler': 'Scaler: Companies with 10%+ growth',
            'High Growth Firm': 'High Growth Firm: Companies with 20%+ growth',
            'Consistent High Growth Firm': 'Consistent High Growth Firm: Consistent 20%+ growth',
            'Consistent Hypergrower': 'Consistent Hypergrower: Consistent 40%+ growth',
            'Gazelle': 'Gazelle: Young high growth firms',
            'Mature High Growth Firm': 'Mature High Growth Firm: Mature high growth firms',
            'Scaleup': 'Scaleup: Young hypergrowers',
            'Superstar': 'Superstar: Mature hypergrowers'
        }
        
        selected_display = st.selectbox(
            'Select growth metric',
            list(metrics_mapping.values()),
            help="Choose which growth metric to visualize"
        )
        
        # Reverse mapping to get the internal metric name
        selected_user_metrics = list(metrics_mapping.keys())[list(metrics_mapping.values()).index(selected_display)]
        
        # Map to the actual column prefix in the dataset
        metrics_to_column = {
            'Scaler': 'Scaler',
            'High Growth Firm': 'HighGrowthFirm',
            'Consistent High Growth Firm': 'ConsistentHighGrowthFirm',
            'Consistent Hypergrower': 'VeryHighGrowthFirm',
            'Gazelle': 'Gazelle',
            'Mature High Growth Firm': 'Mature',
            'Scaleup': 'Scaleup',
            'Superstar': 'Superstar'
        }
        
        selected_metrics = metrics_to_column[selected_user_metrics]
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show meaningful content when no countries are selected
    if not selected_countries:
        st.warning("👆 Please select at least one country to view the data")
        
        # Show a preview of available data
        st.markdown("### Preview of Available Data")
        st.dataframe(df.head(5))
        return
    
    # Filtering data
    filtered_data = df[df['Country'].isin(selected_countries)]
    
    # Analysis Section
    st.markdown(f"### Analysis of {selected_display}")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📈 Trend Analysis", "📊 Comparison"])
    
    with tab1:
        # Enhanced visualization
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Set style
        sns.set_style("whitegrid")
        
        # Use a better color palette
        colors = sns.color_palette("tab10", len(selected_countries))
        
        # Years
        x = [2019, 2020, 2021, 2022, 2023]
        
        # Plotting with improved styling
        for i, country in enumerate(selected_countries):
            country_data = filtered_data[filtered_data['Country'] == country]
            ylist = []
            
            for year in x:
                col_name = f"{selected_metrics} {year} %"
                if col_name in country_data.columns:
                    ylist.append(country_data[col_name].iloc[0] * 100)
                else:
                    ylist.append(np.nan)  # Handle missing data
            
            ax.plot(x, ylist, marker='o', linewidth=2.5, color=colors[i], label=country)
            
            # Add value labels with better positioning
            for j, val in enumerate(ylist):
                if not np.isnan(val):
                    ax.annotate(
                        f"{val:.2f}%", 
                        (x[j], val),
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontweight='bold',
                        fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7)
                    )
        
        # Better styling for the plot
        ax.set_title(f'Trend Analysis: {selected_display} (2019-2023)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Percentage of {selected_user_metrics}s (%)', fontsize=12, fontweight='bold')
        
        # Set y-axis to start from 0 for better perspective
        bottom, top = ax.get_ylim()
        ax.set_ylim(0, top * 1.1)
        
        # Customize x-axis
        ax.set_xticks(x)
        ax.set_xticklabels(x, fontsize=10, fontweight='bold')
        
        # Customize grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Improve legend
        ax.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.15), 
            ncol=min(5, len(selected_countries)),
            frameon=True,
            fancybox=True,
            shadow=True
        )
        
        # Tight layout
        plt.tight_layout()
        
        # Show the plot
        st.pyplot(fig)
        
    
    with tab2:
        # Comparison visualization for the latest year (2023)
        if len(selected_countries) > 1:
            latest_year = 2023
            latest_data = []
            
            for country in selected_countries:
                country_data = filtered_data[filtered_data['Country'] == country]
                try:
                    percentage = country_data[f"{selected_metrics} {latest_year} %"].iloc[0] * 100
                    num_companies = country_data[f"{selected_metrics} {latest_year} Num"].iloc[0]
                    total_obs = country_data[f"{selected_metrics} {latest_year} Obs"].iloc[0]
                    
                    latest_data.append({
                        'Country': country,
                        'Percentage': percentage,
                        'Number': num_companies,
                        'Total': total_obs
                    })
                except (KeyError, IndexError):
                    st.warning(f"Data for {country} in {latest_year} is incomplete.")
            
            if latest_data:
                # Sort by percentage
                latest_data = sorted(latest_data, key=lambda x: x['Percentage'], reverse=True)
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(12, max(6, len(selected_countries) * 0.5)))
                
                countries = [item['Country'] for item in latest_data]
                percentages = [item['Percentage'] for item in latest_data]
                
                # Horizontal bar chart for better readability
                bars = ax.barh(countries, percentages, color=sns.color_palette("tab10", len(countries)))
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(
                        width + 0.3, 
                        bar.get_y() + bar.get_height()/2, 
                        f"{percentages[i]:.2f}%", 
                        ha='left', 
                        va='center',
                        fontweight='bold'
                    )
                
                # Add styling
                ax.set_title(f'Comparison of {selected_user_metrics}s in {latest_year}', fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel(f'Percentage of {selected_user_metrics}s (%)', fontsize=12, fontweight='bold')
                ax.set_xlim(0, max(percentages) * 1.2)  # Give some extra space for labels
                
                # Add grid
                ax.grid(True, linestyle='--', alpha=0.7, axis='x')
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("Insufficient data for comparison in 2023.")
        else:
            st.info("Select at least two countries to view comparison.")
    
    # Footer
    st.markdown('<div class="footer">© European Scaleup Institute. For more information, visit <a href="https://scaleupinstitute.eu/">scaleupinstitute.eu</a></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()