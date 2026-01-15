import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_dashboard():
    # 1. Load Data
    try:
        df = pd.read_csv('natvssynt.csv')
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Create a 2x2 subplot grid
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Virtual Screening Dashboard', fontsize=20, fontweight='bold')

    # Color mapping
    colors = {'Natural': 'skyblue', 'Synthetic': 'orange'}
    
    # --------------------------------------------------------------------------
    # Graph 1: "The Duel" (Avg Score by Type)
    # --------------------------------------------------------------------------
    ax1 = axes[0, 0]
    avg_scores = df.groupby('Type')['Score'].mean()
    
    bars = ax1.bar(avg_scores.index, avg_scores.values, color=[colors[t] for t in avg_scores.index])
    ax1.set_title('Average Binding Affinity (Lower is Better)', fontsize=14)
    ax1.set_ylabel('Score')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                '%.2f' % height,
                ha='center', va='bottom')

    # --------------------------------------------------------------------------
    # Graph 2: "The Leaderboard" (Best to Worst)
    # --------------------------------------------------------------------------
    ax2 = axes[0, 1]
    # Sort by Score (ascending because negative is better)
    df_sorted = df.sort_values('Score', ascending=True)
    
    y_pos = np.arange(len(df_sorted))
    bar_colors = [colors[t] for t in df_sorted['Type']]
    
    ax2.barh(y_pos, df_sorted['Score'], color=bar_colors)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(df_sorted['Name'])
    ax2.invert_yaxis()  # Labels read top-to-bottom
    ax2.set_title('Compound Leaderboard (Top Binders First)', fontsize=14)
    ax2.set_xlabel('Score')
    ax2.grid(axis='x', linestyle='--', alpha=0.7)

    # --------------------------------------------------------------------------
    # Graph 3: "Chemical Space" (MW vs LogP)
    # --------------------------------------------------------------------------
    ax3 = axes[1, 0]
    for c_type, color in colors.items():
        subset = df[df['Type'] == c_type]
        # Size proportional to Score magnitude (abs value)
        sizes = subset['Score'].abs() * 20
        ax3.scatter(subset['Molecular Weight'], subset['LogP'], s=sizes, c=color, label=c_type, alpha=0.7, edgecolors='black')
        
    ax3.set_title('Chemical Space (MW vs LogP)', fontsize=14)
    ax3.set_xlabel('Molecular Weight')
    ax3.set_ylabel('LogP')
    ax3.legend()
    ax3.grid(True, linestyle='--', alpha=0.5)
    
    # Add labels for points
    for i in range(df.shape[0]):
        ax3.text(df['Molecular Weight'][i]+2, df['LogP'][i], df['Name'][i], fontsize=8)

    # --------------------------------------------------------------------------
    # Graph 4: "Size vs Strength" (MW vs Score)
    # --------------------------------------------------------------------------
    ax4 = axes[1, 1]
    
    # Scatter points
    for c_type, color in colors.items():
        subset = df[df['Type'] == c_type]
        ax4.scatter(subset['Molecular Weight'], subset['Score'], c=color, label=c_type, s=80, edgecolors='black')

    # Trend line
    z = np.polyfit(df['Molecular Weight'], df['Score'], 1)
    p = np.poly1d(z)
    x_range = np.linspace(df['Molecular Weight'].min(), df['Molecular Weight'].max(), 100)
    ax4.plot(x_range, p(x_range), "r--", alpha=0.8, label='Trend')
    
    ax4.set_title('Size vs Strength Correlation', fontsize=14)
    ax4.set_xlabel('Molecular Weight')
    ax4.set_ylabel('Score')
    ax4.legend()
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make room for suptitle
    
    output_file = 'dashboard.png'
    plt.savefig(output_file, dpi=300)
    print(f"Dashboard saved to {output_file}")

if __name__ == "__main__":
    create_dashboard()
