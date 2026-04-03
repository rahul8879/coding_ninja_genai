import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def create_supervised_vs_unsupervised_comparison(data, output_file='supervised_vs_unsupervised.png'):
    """
    Create side-by-side comparison showing:
    - LEFT: Supervised (colored by actual labels)
    - RIGHT: Unsupervised (colored by clusters found automatically)
    
    This VISUALLY shows the difference!
    """
    
    # Clean data
    df = data.copy()
    df = df[(df['CIBIL_Score'] >= 300) & (df['CIBIL_Score'] <= 900)]
    df = df[df['Monthly_Income'] > 0]
    
    # Remove outliers
    for col in ['Monthly_Income', 'CIBIL_Score']:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df = df[(df[col] >= Q1 - 3*IQR) & (df[col] <= Q3 + 3*IQR)]
    
    df = df.reset_index(drop=True)
    
    # Prepare features
    X = df[['Monthly_Income', 'CIBIL_Score']].values
    
    # Scale for clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Unsupervised: Find 3 clusters automatically
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    # ==================================================
    # LEFT: SUPERVISED LEARNING (We know the labels)
    # ==================================================
    
    approved = df[df['Loan_Status'] == 'Approved']
    rejected = df[df['Loan_Status'] == 'Rejected']
    
    ax1.scatter(rejected['Monthly_Income'], rejected['CIBIL_Score'],
               c='#E74C3C', s=100, alpha=0.7, label='Rejected',
               edgecolors='white', linewidths=1)
    ax1.scatter(approved['Monthly_Income'], approved['CIBIL_Score'],
               c='#27AE60', s=100, alpha=0.7, label='Approved',
               edgecolors='white', linewidths=1)
    
    ax1.set_title('SUPERVISED LEARNING\n(We have LABELS: Approved/Rejected)', 
                 fontsize=16, weight='bold', pad=15, color='#2C3E50')
    ax1.set_xlabel('Monthly Income (₹)', fontsize=13, weight='bold')
    ax1.set_ylabel('CIBIL Score', fontsize=13, weight='bold')
    ax1.legend(fontsize=12, loc='upper left', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_facecolor('#F8F9F9')
    
    # Add annotation
    ax1.text(0.5, 0.02, 
            '✓ Algorithm learns from LABELED examples\n✓ Task: Predict label for new customer',
            transform=ax1.transAxes, fontsize=11, ha='center',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#D5F4E6', 
                     edgecolor='#27AE60', linewidth=2, alpha=0.9))
    
    # ==================================================
    # RIGHT: UNSUPERVISED LEARNING (No labels!)
    # ==================================================
    
    # Color by cluster
    colors = ['#3498DB', '#E67E22', '#9B59B6']
    cluster_names = ['Group 1: Risky', 'Group 2: Standard', 'Group 3: Premium']
    
    for i in range(3):
        mask = clusters == i
        ax2.scatter(df.loc[mask, 'Monthly_Income'], 
                   df.loc[mask, 'CIBIL_Score'],
                   c=colors[i], s=100, alpha=0.7, 
                   label=cluster_names[i],
                   edgecolors='white', linewidths=1)
    
    # Plot cluster centers
    centers_original = scaler.inverse_transform(kmeans.cluster_centers_)
    ax2.scatter(centers_original[:, 0], centers_original[:, 1],
               c='black', s=400, marker='X', 
               edgecolors='yellow', linewidths=3,
               label='Cluster Centers', zorder=10)
    
    ax2.set_title('UNSUPERVISED LEARNING\n(NO LABELS - Algorithm finds groups itself!)', 
                 fontsize=16, weight='bold', pad=15, color='#2C3E50')
    ax2.set_xlabel('Monthly Income (₹)', fontsize=13, weight='bold')
    ax2.set_ylabel('CIBIL Score', fontsize=13, weight='bold')
    ax2.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_facecolor('#F8F9F9')
    
    # Add annotation
    ax2.text(0.5, 0.02,
            '✓ NO labels given to algorithm\n✓ Task: Find natural groupings in data',
            transform=ax2.transAxes, fontsize=11, ha='center',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='#FCF3CF',
                     edgecolor='#F39C12', linewidth=2, alpha=0.9))
    
    # Main title
    fig.suptitle('SUPERVISED vs UNSUPERVISED Learning\nSame Data, Different Approaches!',
                fontsize=18, weight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_file, dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Comparison saved: {output_file}")
    
    # Print cluster statistics
    print("\n📊 UNSUPERVISED Learning Results:")
    print("=" * 50)
    for i in range(3):
        mask = clusters == i
        cluster_data = df[mask]
        print(f"\n{cluster_names[i]}:")
        print(f"  Count: {mask.sum()} customers")
        print(f"  Avg Income: ₹{cluster_data['Monthly_Income'].mean():,.0f}")
        print(f"  Avg CIBIL: {cluster_data['CIBIL_Score'].mean():.0f}")
        
        # Show how many were actually approved/rejected
        approved_in_cluster = (cluster_data['Loan_Status'] == 'Approved').sum()
        rejected_in_cluster = (cluster_data['Loan_Status'] == 'Rejected').sum()
        print(f"  (Actually: {approved_in_cluster} Approved, {rejected_in_cluster} Rejected)")
    
    return output_file


if __name__ == "__main__":
    print("Supervised vs Unsupervised Comparison Generator")
    print("Usage: create_supervised_vs_unsupervised_comparison(data)")