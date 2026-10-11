"""Vẽ Hình 4.1 – 4.7 của Chương 4 (EDA).
Cần: transactions_cleaned.csv, customer_features.csv (cùng thư mục, hoặc sửa đường dẫn bên dưới).
Chạy: python ve_bieu_do_chuong4.py   ->  ảnh lưu trong thư mục fig/
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TX_PATH = 'transactions_cleaned.csv'
FEAT_PATH = 'customer_features.csv'
OUT = 'fig'
T = pd.Timestamp('2011-06-01')      # ngày dự báo t
H = 180                             # cửa sổ nhãn (ngày)
REF = pd.Timestamp('2011-12-10')    # ngày chốt Recency toàn lịch sử
NAVY, OR = '#274b73', '#b5622b'
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
os.makedirs(OUT, exist_ok=True)

def clean(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

# ---------------- 1. Chuẩn bị dữ liệu ----------------
df = pd.read_csv(TX_PATH, dtype={'Invoice': str, 'StockCode': str})
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
# làm sạch theo notebook 01: bỏ dòng trùng, bỏ mã phí/điều chỉnh -> 776.857 dòng mua
codes = {x.upper() for x in ['POST','DOT','M','D','S','BANK CHARGES','ADJUST','AMAZONFEE','CRUK','B','GIFT']}
d = df.drop_duplicates()
d = d[~d.StockCode.str.upper().isin(codes)].copy()
d['Rev'] = d.Quantity * d.Price
d['cid'] = d['Customer ID'].astype(int)

# bảng toàn lịch sử (5.853 khách)
c = d.groupby('cid').agg(last=('InvoiceDate', 'max'), F=('Invoice', 'nunique'), M=('Rev', 'sum'))
c['R'] = (REF - c['last'].dt.normalize()).dt.days

# phân khúc RFM (ngũ phân vị trên thứ hạng)
def rk(x, asc=True):
    return pd.qcut(x.rank(method='first', ascending=asc), 5, labels=[1,2,3,4,5]).astype(int)
c['r'], c['f'], c['m'] = rk(c.R, False), rk(c.F), rk(c.M)
c['fm'] = (c.f + c.m) / 2
def seg(x):
    if x.r >= 4 and x.fm >= 4: return 'Champions'
    if x.r >= 3 and x.fm >= 3: return 'Loyal'
    if x.r >= 4: return 'New / Promising'
    if x.r == 3: return 'Need Attention'
    if x.r <= 2 and x.fm >= 3.5: return 'At Risk (giá trị cao)'
    if x.r == 2: return 'About to Sleep'
    return 'Lost'
c['seg'] = c.apply(seg, axis=1)

# doanh thu / khách hoạt động theo tháng
d['ym'] = d.InvoiceDate.dt.to_period('M')
mo = d.groupby('ym').agg(rev=('Rev', 'sum'), cust=('cid', 'nunique'))

# bảng mô hình (2.658 khách) + nhãn churn tương lai
cf = pd.read_csv(FEAT_PATH)
cf['cid'] = cf['Customer ID'].astype(int)
fut = d[(d.InvoiceDate >= T) & (d.InvoiceDate < T + pd.Timedelta(days=H))]
cf['is_churn'] = (~cf.cid.isin(set(fut.cid))).astype(int)
print('churn:', cf.is_churn.sum(), '/', len(cf))   # kỳ vọng 804 / 2658

# ---------------- Hình 4.1 ----------------
fig, ax = plt.subplots(figsize=(8, 3.6)); x = np.arange(len(mo))
b = ax.bar(x, mo.rev/1000, color=NAVY); b[-1].set_alpha(.45)      # tháng 12/2011 chỉ đến 09/12
ax.set_ylabel('Doanh thu (nghìn GBP)')
ax.set_xticks(x[::2]); ax.set_xticklabels([str(p) for p in mo.index[::2]], rotation=45, ha='right')
ax2 = ax.twinx(); ax2.plot(x, mo.cust, color=OR, marker='o', ms=3)
ax2.set_ylabel('Số khách hàng hoạt động', color=OR)
ax.set_title('Doanh thu hóa đơn mua và số khách hàng hoạt động theo tháng')
clean(ax); ax2.spines['top'].set_visible(False)
plt.tight_layout(); plt.savefig(f'{OUT}/f41.png', dpi=200); plt.close()

# ---------------- Hình 4.2 ----------------
fig, axs = plt.subplots(1, 3, figsize=(9, 2.8))
axs[0].hist(c.R, bins=40, color=NAVY); axs[0].axvline(180, color=OR, ls='--')
axs[0].text(190, axs[0].get_ylim()[1]*.9, '180 ngày', color=OR)
axs[0].set_xlabel('Recency (ngày)'); axs[0].set_ylabel('Số khách hàng')
axs[1].hist(c.F, bins=np.logspace(0, np.log10(c.F.max()+1), 30), color=NAVY)
axs[1].set_xscale('log'); axs[1].set_xlabel('Frequency (thang log)')
axs[2].hist(c.M, bins=np.logspace(np.log10(c.M.min()), np.log10(c.M.max()), 30), color=NAVY)
axs[2].set_xscale('log'); axs[2].set_xlabel('Chi tiêu mua hàng (GBP, thang log)')
for a in axs: clean(a)
plt.tight_layout(); plt.savefig(f'{OUT}/f42.png', dpi=200); plt.close()

# ---------------- Hình 4.3 (Pareto) ----------------
s = np.sort(c.M.values)[::-1]
cs = np.r_[0, np.cumsum(s)/s.sum()] * 100; xp = np.linspace(0, 100, len(cs))
k = int(round(len(s)*.2))
fig, ax = plt.subplots(figsize=(5.2, 4))
ax.plot(xp, cs, color=NAVY, lw=2); ax.plot([0,100], [0,100], ls=':', color='gray')
ax.scatter([20], [cs[k]], color=OR, zorder=5)
ax.annotate(f'20% khách hàng đầu\n→ {cs[k]:.1f}% doanh thu'.replace('.', ','), (20, cs[k]), (38, 58),
            arrowprops=dict(arrowstyle='->', color=OR), color=OR)
ax.set_xlabel('% khách hàng (xếp từ chi tiêu cao xuống thấp)'); ax.set_ylabel('% doanh thu tích lũy')
ax.set_title('Đường cong Pareto của doanh thu'); clean(ax)
plt.tight_layout(); plt.savefig(f'{OUT}/f43.png', dpi=200); plt.close()

# ---------------- Hình 4.4 (phân khúc RFM) ----------------
order = ['Champions','Loyal','New / Promising','Need Attention','At Risk (giá trị cao)','About to Sleep','Lost']
sg = c.groupby('seg').agg(n=('R','size'), rev=('M','sum')).loc[order]
pn, pr = sg.n/sg.n.sum()*100, sg.rev/sg.rev.sum()*100
fig, ax = plt.subplots(figsize=(7, 3.6)); y = np.arange(len(order))[::-1]; h = .38
ax.barh(y+h/2, pn, h, color=NAVY, label='% số khách hàng')
ax.barh(y-h/2, pr, h, color=OR, label='% doanh thu')
for yy, a_, b_ in zip(y, pn, pr):
    ax.text(a_+.5, yy+h/2, f'{a_:.1f}'.replace('.', ','), va='center', fontsize=7)
    ax.text(b_+.5, yy-h/2, f'{b_:.1f}'.replace('.', ','), va='center', fontsize=7)
ax.set_yticks(y); ax.set_yticklabels(order); ax.set_xlabel('%')
ax.legend(frameon=False, loc='lower right'); ax.set_title('Tỷ trọng khách hàng và doanh thu theo phân khúc RFM'); clean(ax)
plt.tight_layout(); plt.savefig(f'{OUT}/f44.png', dpi=200); plt.close()

# ---------------- Hình 4.5 (boxplot theo nhãn churn) ----------------
fig, axs = plt.subplots(1, 4, figsize=(9.5, 3.2))
for a, (col, t) in zip(axs, [('Frequency','Frequency'), ('Monetary','Monetary (GBP)'),
                             ('AvgOrderValue','AvgOrderValue (GBP)'), ('UniqueProducts','UniqueProducts')]):
    data = [cf[(cf.is_churn == k_) & (cf[col] > 1)][col] for k_ in (0, 1)]   # bỏ giá trị <= 1 để vẽ thang log
    bp = a.boxplot(data, patch_artist=True, showfliers=False, medianprops=dict(color='white', lw=1.5), widths=.6)
    for p, cl in zip(bp['boxes'], [NAVY, OR]): p.set_facecolor(cl); p.set_edgecolor(cl)
    a.set_yscale('log'); a.set_xticklabels(['Không churn', 'Churn']); a.set_title(t, fontsize=9); clean(a)
plt.tight_layout(); plt.savefig(f'{OUT}/f45.png', dpi=200); plt.close()

# ---------------- Hình 4.6 (ma trận Spearman) ----------------
F = ['Recency','Frequency','Monetary','AvgOrderValue','TotalItems','UniqueProducts','is_churn']
cm = cf[F].corr(method='spearman')
fig, ax = plt.subplots(figsize=(6.2, 5.2)); im = ax.imshow(cm, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(7)); ax.set_yticks(range(7))
ax.set_xticklabels(F, rotation=40, ha='right'); ax.set_yticklabels(F)
for i in range(7):
    for j in range(7):
        v = cm.iloc[i, j]
        ax.text(j, i, f'{v:.2f}'.replace('.', ','), ha='center', va='center', fontsize=8,
                color='white' if abs(v) > .55 else 'black')
plt.colorbar(im, fraction=.046); ax.set_title('Ma trận tương quan Spearman (n = 2.658)')
plt.tight_layout(); plt.savefig(f'{OUT}/f46.png', dpi=200); plt.close()

# ---------------- Hình 4.7 (tỷ lệ churn theo Frequency / Monetary) ----------------
fg = pd.cut(cf.Frequency, [0,1,2,3,5,10,1000], labels=['1','2','3','4–5','6–10','>10'])
r1 = cf.groupby(fg, observed=True).is_churn.mean()*100
q = pd.qcut(cf.Monetary.rank(method='first'), 5, labels=['Q1\n(thấp)','Q2','Q3','Q4','Q5\n(cao)'])
r2 = cf.groupby(q, observed=True).is_churn.mean()*100
ov = cf.is_churn.mean()*100
fig, axs = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
for a, r, xl in [(axs[0], r1, 'Số hóa đơn (Frequency)'), (axs[1], r2, 'Nhóm ngũ phân vị Monetary')]:
    a.bar(range(len(r)), r.values, color=NAVY, width=.6); a.axhline(ov, color=OR, ls='--', lw=1)
    for i, v in enumerate(r.values): a.text(i, v+1, f'{v:.1f}%'.replace('.', ','), ha='center', fontsize=8)
    a.set_xticks(range(len(r))); a.set_xticklabels(list(r.index)); a.set_xlabel(xl); clean(a)
axs[0].set_ylabel('Tỷ lệ churn (%)'); axs[0].set_ylim(0, 70)
plt.tight_layout(); plt.savefig(f'{OUT}/f47.png', dpi=200); plt.close()
print('Xong: 7 hình trong', OUT)