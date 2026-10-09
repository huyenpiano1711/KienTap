# Hướng dẫn chia việc & cấu trúc GitHub — Chương 3 & 4

## Cấu trúc thư mục repo đề xuất

```
kien-tap-churn-crm/
├── data/
│   ├── raw/
│   │   └── online_retail_II.csv          ← file gốc từ Kaggle, KHÔNG ai chỉnh sửa
│   ├── interim/
│   │   ├── transactions_cleaned.csv      ← output của 3.2
│   │   └── customer_base.csv             ← output của 3.3
│   └── processed/
│       ├── customer_features.csv         ← output của 3.4
│       └── customer_features_labeled.csv ← output của 3.5 (file này ai từ 4.1 trở đi đều dùng)
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_customer_aggregation.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_churn_labeling.ipynb
│   ├── 05_model_training.ipynb
│   ├── 06_model_comparison.ipynb
│   ├── 07_feature_importance.ipynb
│   ├── 08_descriptive_stats.ipynb
│   ├── 09_customer_behavior_segmentation.ipynb
│   ├── 10_correlation_analysis.ipynb
│   └── 11_dashboard_data_prep.ipynb
├── models/
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   └── metrics_summary.json              ← Accuracy/Precision/Recall/F1/AUC của cả 3 model
├── reports/
│   └── figures/                          ← mọi biểu đồ .png xuất ra để dán vào báo cáo Word
├── dashboard/
│   └── crm_churn_dashboard.pbix           (hoặc .twbx nếu dùng Tableau)
└── README.md
```

**Quy tắc bắt buộc:** mỗi người khi xong việc phải push đúng 2 thứ — (1) notebook code, (2) file dữ liệu/mô hình output đúng tên như trên — để người tiếp theo trong chuỗi lấy đúng file mà chạy tiếp, không phải hỏi lại nhau.

---

## Mục 3.2 — Nguyên Khôi: `01_data_cleaning.ipynb`

**Input:** `data/raw/online_retail_II.csv`
**Việc làm:** gộp 2 giai đoạn dữ liệu (2009-2010, 2010-2011), kiểm tra & xử lý missing values, loại bỏ dòng thiếu Customer ID, tách/đánh dấu hóa đơn hủy-hoàn trả (Invoice bắt đầu bằng "C"), xử lý outlier (Quantity/Price âm hoặc bất thường).
**Output bắt buộc:** `data/interim/transactions_cleaned.csv` — mỗi dòng vẫn là 1 dòng giao dịch (item-level), đã sạch.
**Ghi chú cho báo cáo:** log lại số dòng trước/sau mỗi bước xử lý (VD: "loại 135.080 dòng thiếu Customer ID") — cần cho phần viết 3.2.

## Mục 3.3 — Nguyên Khôi: `02_customer_aggregation.ipynb`

**Input:** `data/interim/transactions_cleaned.csv`
**Việc làm:** xác định đơn vị phân tích là khách hàng (Customer ID), tổng hợp từ dữ liệu giao dịch thành 1 dòng/khách hàng (tổng số hóa đơn, tổng chi tiêu, ngày mua đầu/cuối...).
**Output bắt buộc:** `data/interim/customer_base.csv` — 1 dòng = 1 khách hàng.

## Mục 3.4 — Quỳnh Kha: `03_feature_engineering.ipynb`

**Input:** `data/interim/customer_base.csv`
**Việc làm:** tính RFM (Recency, Frequency, Monetary) + các biến bổ sung: AvgOrderValue, UniqueProducts, TotalItems, Country.
**Output bắt buộc:** `data/processed/customer_features.csv`

## Mục 3.5 — Quỳnh Kha: `04_churn_labeling.ipynb`

**Input:** `data/processed/customer_features.csv`
**Việc làm:** xác định ngưỡng thời gian không phát sinh giao dịch để gán nhãn churn (VD: > 90 ngày kể từ lần mua cuối = churn), giải thích rõ căn cứ chọn ngưỡng này trong báo cáo.
**Output bắt buộc:** `data/processed/customer_features_labeled.csv` — thêm cột `is_churn` (0/1). **File này là điểm chia nhánh — từ đây Phương Anh, Bảo Duy, Như Huyền có thể làm song song.**

## Mục 3.6 — Như Huyền: `05_model_training.ipynb`

**Input:** `data/processed/customer_features_labeled.csv`
**Việc làm:** chia train/test, xử lý mất cân bằng lớp nếu cần (VD: class_weight hoặc SMOTE), huấn luyện Logistic Regression (baseline), Random Forest, XGBoost.
**Output bắt buộc:** `models/logistic_regression.pkl`, `models/random_forest.pkl`, `models/xgboost.pkl`

## Mục 3.7 — Như Huyền: `11_dashboard_data_prep.ipynb`

**Input:** `data/processed/customer_features_labeled.csv` + kết quả dự đoán từ các model (3.6)
**Việc làm:** chuẩn bị bảng dữ liệu đã format sẵn (điểm rủi ro churn, phân nhóm risk Low/Medium/High, top khách hàng...) để nạp thẳng vào Power BI/Tableau.
**Output bắt buộc:** `data/processed/dashboard_data.csv`

## Mục 4.1 & 4.2 — Phương Anh: `08_descriptive_stats.ipynb`, `09_customer_behavior_segmentation.ipynb`

**Input:** `data/processed/customer_features_labeled.csv` (không cần đợi model — làm song song với 3.6 luôn được)
**Việc làm:** thống kê mô tả (số khách hàng, giao dịch, doanh thu, phân bố RFM); phân khúc khách hàng, so sánh đặc điểm nhóm churn vs không churn.
**Output bắt buộc:** biểu đồ .png lưu vào `reports/figures/`, đặt tên rõ (VD: `rfm_distribution.png`, `churn_vs_nonchurn_comparison.png`)

## Mục 4.3 — Bảo Duy: `10_correlation_analysis.ipynb`

**Input:** `data/processed/customer_features_labeled.csv` (cũng làm song song được, không cần đợi model)
**Việc làm:** ma trận tương quan giữa các biến RFM và churn, nhận xét xu hướng.
**Output bắt buộc:** `reports/figures/correlation_matrix.png`

## Mục 4.4 — Bảo Duy: (dùng chung `05_model_training.ipynb` của Như Huyền)

**Input:** `models/*.pkl` (phải đợi 3.6 xong)
**Việc làm:** trình bày kết quả từng model.
**Output bắt buộc:** `models/metrics_summary.json` (Accuracy/Precision/Recall/F1/AUC mỗi model)

## Mục 4.5 — Bảo Duy: `06_model_comparison.ipynb`

**Input:** `models/metrics_summary.json`
**Việc làm:** lập bảng so sánh, lựa chọn mô hình phù hợp nhất cho bài toán churn (ưu tiên Recall/F1 hơn Accuracy — theo đúng lập luận đã viết ở mục 2.5). **Sau khi chọn xong, áp model đó lên TOÀN BỘ khách hàng** (không chỉ tập test) để tạo danh sách dự đoán thật.
**Output bắt buộc:** `data/processed/churn_predictions.csv` — mỗi khách hàng kèm xác suất churn (`churn_probability`) và nhóm rủi ro (`risk_level`: Low/Medium/High). **File này bắt buộc phải có trước khi làm 3.7 và 4.6.**

## Bổ sung trong Mục 3.6 — Như Huyền: tuning & xử lý mất cân bằng

Trước khi chốt 3 model cuối, thử:
- `class_weight='balanced'` (Logistic Regression, Random Forest) hoặc SMOTE để xử lý việc số khách churn thường ít hơn nhiều so với không churn
- `GridSearchCV`/`RandomizedSearchCV` để tìm tham số tốt hơn cho Random Forest và XGBoost — không dùng tham số mặc định, vì kết quả so sánh ở 4.5 sẽ không thuyết phục nếu chỉ so parameter mặc định.

## Việc chung — Nguyên Khôi: `requirements.txt` + hướng dẫn chạy

Ngay khi khởi tạo repo, Nguyên Khôi tạo file `requirements.txt` (liệt kê pandas, scikit-learn, xgboost, matplotlib... kèm phiên bản) và một đoạn ngắn trong README ghi rõ thứ tự chạy notebook — để ai clone repo về cũng chạy được mà không lỗi thiếu thư viện.

## Mục 4.6 — Quỳnh Kha: `07_feature_importance.ipynb`

**Input:** `models/random_forest.pkl` hoặc `models/xgboost.pkl` (model đã chọn ở 4.5)
**Việc làm:** trích xuất & vẽ biểu đồ feature importance, diễn giải ý nghĩa kinh doanh của từng yếu tố quan trọng nhất.
**Output bắt buộc:** `reports/figures/feature_importance.png`

## Mục 4.7 — Bảo Duy (phối hợp Như Huyền): `dashboard/crm_churn_dashboard.pbix`

**Input:** `data/processed/dashboard_data.csv` (từ 3.7)
**Việc làm:** dựng dashboard Power BI/Tableau — tổng quan khách hàng, phân khúc, churn risk, doanh thu, top customers.
**Output bắt buộc:** file `.pbix`/`.twbx` + ảnh chụp màn hình dashboard cho vào `reports/figures/dashboard_screenshot.png` (dùng để dán vào báo cáo Word).

---

## Thứ tự làm việc đề xuất (rút ngắn thời gian)

1. **Ngay bây giờ:** Nguyên Khôi bắt đầu 3.2 → 3.3 (đường găng, mọi người khác phải đợi file `customer_base.csv`)
2. **Ngay sau khi 3.3 xong:** Quỳnh Kha làm 3.4 → 3.5
3. **Ngay sau khi 3.5 xong (`customer_features_labeled.csv` có mặt):** ba việc chạy **song song**:
   - Như Huyền: 3.6 (train model) — ưu tiên cao nhất vì 4.4/4.5/4.6/4.7 đều phụ thuộc vào đây
   - Phương Anh: 4.1, 4.2
   - Bảo Duy: 4.3
4. **Sau khi 3.6 xong:** Bảo Duy làm 4.4 → 4.5 liền mạch (đã có metrics sẵn), xuất `churn_predictions.csv`
5. **Sau khi có `churn_predictions.csv`:** Như Huyền làm 3.7, Quỳnh Kha làm 4.6 — chạy song song
6. **Sau khi 3.7 xong:** Bảo Duy dựng dashboard 4.7

## Việc chung, không thuộc từng mục

- **Nguyên Khôi**, ngay khi khởi tạo repo: tạo `requirements.txt` (pandas, scikit-learn, xgboost, matplotlib... kèm phiên bản) + đoạn hướng dẫn chạy notebook theo thứ tự trong README, để ai clone về cũng chạy được.
- **Như Huyền**, trong lúc làm 3.6: thử `class_weight='balanced'`/SMOTE cho dữ liệu mất cân bằng, và `GridSearchCV`/`RandomizedSearchCV` để tune tham số Random Forest & XGBoost — đừng chỉ dùng tham số mặc định, vì bảng so sánh ở 4.5 sẽ không thuyết phục nếu vậy.

## Hướng dẫn cài đặt và chạy môi trường (Setup Guide)

1. Cài đặt các thư viện bắt buộc bằng lệnh: 
   `pip install -r requirements.txt`
2. Đảm bảo file gốc `online_retail_II.csv` đã được đặt vào thư mục `data/raw/` trước khi chạy code.
3. Chạy các file Jupyter Notebook trong thư mục `notebooks/` theo đúng thứ tự đánh số từ `01_...` đến `11_...` để tránh lỗi thiếu file Input do chạy nhảy cóc.
