import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from PIL import Image
import io

def clean_loan_data(data):
    """Clean data"""
    df = data.copy()
    df = df[(df['CIBIL_Score'] >= 300) & (df['CIBIL_Score'] <= 900)]
    df = df[df['Monthly_Income'] > 0]
    
    for col in ['Monthly_Income', 'CIBIL_Score']:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df = df[(df[col] >= Q1 - 3*IQR) & (df[col] <= Q3 + 3*IQR)]
    
    return df.reset_index(drop=True)


def create_knn_gif_clean(data,new_cut, output_file='knn_vibrant.gif'):
    """
    KNN GIF with HIGH CONTRAST colors for better visibility
    
    Color scheme:
    - Rejected: Dark Blue (#2E86C1) - clearly visible
    - Approved: Dark Orange (#E67E22) - clearly visible  
    - New Customer: Bright Red (#E74C3C) - stands out
    - Lines: Bold and thick
    - Background: White (maximum contrast)
    """
    
    df = clean_loan_data(data)
    approved = df[df['Loan_Status'] == 'Approved']
    rejected = df[df['Loan_Status'] == 'Rejected']
    
    # Pick boundary customer
    boundary = rejected[
        (rejected['CIBIL_Score'] > rejected['CIBIL_Score'].quantile(0.4)) &
        (rejected['CIBIL_Score'] < rejected['CIBIL_Score'].quantile(0.6))
    ]
    idx = boundary.sample(1).index[0] if len(boundary) > 0 else rejected.sample(1).index[0]

    new_pt = new_cut
    # Feature scaling
    scaler = StandardScaler()
    features = df[['Monthly_Income', 'CIBIL_Score']].values
    scaled_features = scaler.fit_transform(features)
    new_pt_scaled = scaler.transform([[new_pt[0], new_pt[1]]])[0]
    
    # Calculate distances (scaled)
    distances = []
    for i, (idx_val, row) in enumerate(df.iterrows()):
        if idx_val == idx:
            continue
        scaled_pt = scaled_features[i]
        dist = np.sqrt((scaled_pt[0] - new_pt_scaled[0])**2 + 
                      (scaled_pt[1] - new_pt_scaled[1])**2)
        distances.append({
            'd': dist,
            'x': row['Monthly_Income'],
            'y': row['CIBIL_Score'],
            's': row['Loan_Status']
        })
    
    distances = sorted(distances, key=lambda x: x['d'])
    
    # HIGH CONTRAST COLOR PALETTE
    COLORS = {
        'rejected_bg': '#AED6F1',      # Light blue background
        'rejected_main': '#2E86C1',    # Dark blue main
        'rejected_line': '#1F618D',    # Darker blue for lines
        'approved_bg': '#F8C471',      # Light orange background
        'approved_main': '#E67E22',    # Dark orange main
        'approved_line': '#D35400',    # Darker orange for lines
        'new_customer': '#E74C3C',     # Bright red
        'new_edge': '#000000',         # Black edge
    }
    
    frames = []
    k_values = [1, 3, 5, 7, 10, 15, 20]
    
    print("Creating vibrant GIF...\n")
    
    for k in k_values:
        fig, ax = plt.subplots(figsize=(14, 9))
        
        # WHITE background for maximum contrast
        ax.set_facecolor('#FFFFFF')
        fig.patch.set_facecolor('#FFFFFF')
        
        # Background dots - LARGER and more visible
        ax.scatter(rejected['Monthly_Income'], rejected['CIBIL_Score'], 
                  c=COLORS['rejected_bg'], s=100, alpha=0.5, 
                  edgecolors=COLORS['rejected_main'], linewidths=0.5,
                  label='Rejected', zorder=1)
        ax.scatter(approved['Monthly_Income'], approved['CIBIL_Score'], 
                  c=COLORS['approved_bg'], s=100, alpha=0.5,
                  edgecolors=COLORS['approved_main'], linewidths=0.5,
                  label='Approved', zorder=1)
        
        # K neighbors
        neighbors = distances[:k]
        
        # THICK lines with dark colors
        for n in neighbors:
            if n['s'] == 'Approved':
                line_color = COLORS['approved_line']
            else:
                line_color = COLORS['rejected_line']
            
            ax.plot([new_pt[0], n['x']], [new_pt[1], n['y']], 
                   color=line_color, linewidth=3.5, alpha=0.8, zorder=3)
        
        # Highlighted neighbors - BOLD colors
        for n in neighbors:
            if n['s'] == 'Approved':
                color = COLORS['approved_main']
                edge = COLORS['approved_line']
            else:
                color = COLORS['rejected_main']
                edge = COLORS['rejected_line']
            
            ax.scatter(n['x'], n['y'], c=color, s=250, 
                      edgecolors=edge, linewidths=3, zorder=6)
        
        # New customer - VERY VISIBLE
        ax.scatter(new_pt[0], new_pt[1], 
                  c=COLORS['new_customer'], s=500, marker='P', 
                  edgecolors=COLORS['new_edge'], linewidths=4, 
                  zorder=10, label='New Customer')
        
        # Vote count
        app = sum(1 for n in neighbors if n['s'] == 'Approved')
        rej = k - app
        
        if app > rej:
            decision = "✓ APPROVED"
            decision_color = '#27AE60'  # Green
            box_color = '#ABEBC6'
        else:
            decision = "✗ REJECTED"
            decision_color = '#C0392B'  # Red
            box_color = '#F5B7B1'
        
        # K display - BIGGER and BOLDER
        ax.text(0.97, 0.97, f'K = {k}', 
               transform=ax.transAxes, 
               fontsize=28, weight='bold', 
               ha='right', va='top',
               color='#000000',
               bbox=dict(boxstyle='round,pad=0.8', 
                        facecolor='#F4D03F', 
                        edgecolor='#000000', 
                        linewidth=3, alpha=0.95))
        
        # Vote count box
        vote_text = f'Approved: {app}\nRejected: {rej}'
        ax.text(0.03, 0.97, vote_text, 
               transform=ax.transAxes, 
               fontsize=16, weight='bold',
               ha='left', va='top',
               bbox=dict(boxstyle='round,pad=0.6', 
                        facecolor='#ECF0F1', 
                        edgecolor='#000000', 
                        linewidth=2, alpha=0.95))
        
        # Title - BOLD and CLEAR
        title = f'{decision}\nIs it magic ??'
        ax.set_title(title, 
                    fontsize=18, weight='bold', 
                    color=decision_color, 
                    pad=15,
                    bbox=dict(boxstyle='round,pad=0.8', 
                             facecolor=box_color,
                             edgecolor=decision_color,
                             linewidth=3))
        
        ax.set_xlabel('Monthly Income (₹)', fontsize=14, weight='bold')
        ax.set_ylabel('CIBIL Score', fontsize=14, weight='bold')
        
        # Legend with better styling
        legend = ax.legend(loc='upper right', fontsize=11, 
                          framealpha=0.95, edgecolor='black', 
                          fancybox=True, shadow=True)
        legend.get_frame().set_linewidth(2)
        
        # Grid - subtle
        ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        # Save frame
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        frames.append(Image.open(buf).copy())
        plt.close()
        
        print(f"  ✓ K={k}: {decision}")
    
    # Save GIF
    frames[0].save(output_file, save_all=True, append_images=frames[1:], 
                   duration=1300, loop=0)
    
    print(f"\n✅ Vibrant GIF saved: {output_file}")
    print(f"   Color scheme: High contrast for better visibility")
    return output_file


if __name__ == "__main__":
    print("KNN GIF - High Contrast Version")
    print("=" * 50)