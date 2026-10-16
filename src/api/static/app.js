// ============================================================================
// Enterprise BFSI Customer 360 Dashboard Logic
// ============================================================================

let currentTab = "tab-overview";
let chartMonthlyVolume = null;
let chartSegments = null;
let chartSegmentRisk = null;
let chartProductHoldings = null;

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadExecutiveKPIs();
  loadOverviewCharts();
  loadCustomers();
  loadBusinessQuestion(1);
  loadDataQualityReport();
});

// Navigation Handling
function initNavigation() {
  document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
      const tabId = item.getAttribute("data-tab");
      if (!tabId) return;

      document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
      item.classList.add("active");

      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
      const activePane = document.getElementById(tabId);
      if (activePane) activePane.classList.add("active");

      currentTab = tabId;

      // Update Header Title
      const titles = {
        "tab-overview": { title: "Executive Banking Overview", sub: "Consolidated 360° analytics across Accounts, Loans, Cards, Transactions & Omnichannel CRM" },
        "tab-c360": { title: "Customer 360 Profile Explorer", sub: "Search and inspect 1,200 unified customer records with full relationship depth" },
        "tab-bq": { title: "Business Questions Analytics Workbench", sub: "Direct production SQL analytical answers for high-value segments, NPLs, and engagement" },
        "tab-governance": { title: "Data Quality & Governance Layer", sub: "15 automated validation rules ensuring zero schema drift, orphan accounts, or data violations" },
        "tab-lineage": { title: "End-to-End Data Lineage Architecture", sub: "Operational Sources → ETL Ingestion → DQ Validation → EDW Star Schema → Serving Mart" },
        "tab-powerbi": { title: "BI Integration Hub — Power BI & Tableau", sub: "Semantic models, certified DAX measures & Tableau calculated fields, one-click data exports" }
      };

      if (titles[tabId]) {
        document.getElementById("page-title").textContent = titles[tabId].title;
        document.getElementById("page-subtitle").textContent = titles[tabId].sub;
      }
    });
  });
}

// 1. Executive KPIs
async function loadExecutiveKPIs() {
  try {
    const res = await fetch("/api/analytics/kpis");
    const data = await res.json();
    const p = data.portfolio_summary;

    document.getElementById("kpi-total-cust").textContent = Number(p.total_customers).toLocaleString();
    document.getElementById("badge-cust-count").textContent = `${(p.total_customers / 1000).toFixed(1)}K`;
    document.getElementById("kpi-total-deposits").textContent = `$${(p.total_deposits / 1e6).toFixed(2)}M`;
    document.getElementById("kpi-total-loans").textContent = `$${(p.total_loans_outstanding / 1e6).toFixed(2)}M`;
    document.getElementById("kpi-total-overdue").textContent = `$${(p.total_overdue_amount / 1e3).toFixed(1)}K`;
    document.getElementById("kpi-npl-rate").textContent = `NPL Rate: ${p.npl_ratio_pct}%`;
    document.getElementById("kpi-txn-volume").textContent = `$${(p.volume_30d / 1e6).toFixed(2)}M`;
    document.getElementById("kpi-txn-count").textContent = `${Number(p.transactions_30d).toLocaleString()} txns`;
    document.getElementById("kpi-cross-ratio").textContent = `${p.multi_product_penetration_pct}%`;
  } catch (err) {
    console.error("Failed to load KPIs:", err);
  }
}

// 2. Charts for Executive Overview
async function loadOverviewCharts() {
  try {
    // A. Monthly Transactions
    const resTxn = await fetch("/api/analytics/business-questions/monthly-transactions");
    const dataTxn = await resTxn.json();
    const months = dataTxn.monthly_trends.map(m => m.period);
    const volumes = dataTxn.monthly_trends.map(m => m.total_volume / 1000);
    const debitVols = dataTxn.monthly_trends.map(m => m.debit_volume / 1000);
    const creditVols = dataTxn.monthly_trends.map(m => m.credit_volume / 1000);

    const ctxMonthly = document.getElementById("chart-monthly-volume").getContext("2d");
    if (chartMonthlyVolume) chartMonthlyVolume.destroy();
    chartMonthlyVolume = new Chart(ctxMonthly, {
      type: "bar",
      data: {
        labels: months,
        datasets: [
          {
            label: "Debit Volume ($k)",
            data: debitVols,
            backgroundColor: "rgba(6, 182, 212, 0.75)",
            borderRadius: 4
          },
          {
            label: "Credit Volume ($k)",
            data: creditVols,
            backgroundColor: "rgba(99, 102, 241, 0.75)",
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8" } }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });

    // B. Segment Distribution
    const resSeg = await fetch("/api/analytics/business-questions/high-risk-segments");
    const dataSeg = await resSeg.json();
    const segLabels = dataSeg.segments.map(s => s.customer_segment);
    const segCounts = dataSeg.segments.map(s => s.total_customers);

    const ctxSeg = document.getElementById("chart-segments").getContext("2d");
    if (chartSegments) chartSegments.destroy();
    chartSegments = new Chart(ctxSeg, {
      type: "doughnut",
      data: {
        labels: segLabels,
        datasets: [{
          data: segCounts,
          backgroundColor: ["#06b6d4", "#6366f1", "#10b981", "#f59e0b", "#a855f7"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right", labels: { color: "#94a3b8" } }
        }
      }
    });

    // C. Risk Matrix
    const ctxRisk = document.getElementById("chart-segment-risk").getContext("2d");
    if (chartSegmentRisk) chartSegmentRisk.destroy();
    chartSegmentRisk = new Chart(ctxRisk, {
      type: "radar",
      data: {
        labels: segLabels,
        datasets: [
          {
            label: "Composite Risk Score (0-100)",
            data: dataSeg.segments.map(s => s.avg_composite_risk_score),
            borderColor: "rgba(244, 63, 94, 0.8)",
            backgroundColor: "rgba(244, 63, 94, 0.2)",
            pointBackgroundColor: "rgba(244, 63, 94, 1)"
          },
          {
            label: "Delinquency Rate %",
            data: dataSeg.segments.map(s => s.delinquency_rate_pct * 3), // scaled for visibility
            borderColor: "rgba(245, 158, 11, 0.8)",
            backgroundColor: "rgba(245, 158, 11, 0.2)",
            pointBackgroundColor: "rgba(245, 158, 11, 1)"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#94a3b8" } }
        },
        scales: {
          r: {
            grid: { color: "rgba(255, 255, 255, 0.08)" },
            pointLabels: { color: "#94a3b8" },
            ticks: { display: false }
          }
        }
      }
    });

    // D. Product Holdings Breakdown
    const resProd = await fetch("/api/analytics/business-questions/multiple-products");
    const dataProd = await resProd.json();
    const prodLabels = dataProd.product_holding_distribution.map(d => `${d.products_held} Products`);
    const prodCounts = dataProd.product_holding_distribution.map(d => d.customer_count);

    const ctxProd = document.getElementById("chart-product-holdings").getContext("2d");
    if (chartProductHoldings) chartProductHoldings.destroy();
    chartProductHoldings = new Chart(ctxProd, {
      type: "bar",
      data: {
        labels: prodLabels,
        datasets: [{
          label: "Customers",
          data: prodCounts,
          backgroundColor: "rgba(16, 185, 129, 0.75)",
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } },
          y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#94a3b8" } }
        }
      }
    });

  } catch (err) {
    console.error("Failed to load charts:", err);
  }
}

// 3. Customer 360 Table & Search
let searchTimeout = null;
function handleCustomerSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadCustomers();
  }, 300);
}

function applyPresetFilter(preset) {
  const segSelect = document.getElementById("filter-segment");
  const riskSelect = document.getElementById("filter-risk");
  
  if (preset === "overdue") {
    loadCustomers({ has_overdue: true });
  } else if (preset === "multi") {
    loadCustomers({ has_multiple_products: true });
  } else if (preset === "high_val") {
    loadCustomers({ is_high_value: true });
  } else if (preset === "declining") {
    loadCustomers({ engagement_status: "DECLINING" });
  } else {
    loadCustomers();
  }
}

async function loadCustomers(extraParams = {}) {
  const tbody = document.getElementById("customers-table-body");
  tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 24px;">Loading Customer 360 Profiles...</td></tr>`;

  const search = document.getElementById("cust-search").value.trim();
  const segment = document.getElementById("filter-segment").value;
  const risk = document.getElementById("filter-risk").value;

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (segment) params.append("segment", segment);
  if (risk) params.append("risk_tier", risk);
  params.append("limit", "50");

  for (const [k, v] of Object.entries(extraParams)) {
    params.append(k, v);
  }

  try {
    const res = await fetch(`/api/c360/customers?${params.toString()}`);
    const data = await res.json();

    if (!data.items || data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 24px; color:var(--text-dim);">No customer profiles matched the search criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.items.map(c => `
      <tr onclick="openCustomerModal('${c.customer_id}')">
        <td style="font-family:monospace; font-weight:700; color:var(--accent-cyan);">${c.customer_id}</td>
        <td style="font-weight:600;">${c.full_name}</td>
        <td><span class="tag-badge tag-info">${c.customer_segment}</span></td>
        <td style="font-weight:700;">${c.credit_score}</td>
        <td>
          <span class="tag-badge ${c.kyc_status === 'VERIFIED' ? 'tag-positive' : 'tag-warning'}">${c.kyc_status}</span>
        </td>
        <td style="font-weight:700; text-align:center;">${c.total_products_held}</td>
        <td style="color:var(--accent-emerald); font-weight:600;">$${Number(c.total_deposit_balance).toLocaleString()}</td>
        <td style="font-weight:600;">$${Number(c.total_loan_outstanding).toLocaleString()}</td>
        <td style="color:${c.max_overdue_days > 0 ? 'var(--accent-rose)' : 'var(--text-muted)'}; font-weight:700;">
          ${c.max_overdue_days > 0 ? `${c.max_overdue_days}d` : '-'}
        </td>
        <td style="font-weight:700;">${c.ltv_score}</td>
        <td>
          <span class="tag-badge ${
            c.risk_tier === 'CRITICAL' ? 'tag-negative' :
            c.risk_tier === 'HIGH' ? 'tag-negative' :
            c.risk_tier === 'MEDIUM' ? 'tag-warning' : 'tag-positive'
          }">${c.risk_tier}</span>
        </td>
        <td>
          <button class="btn btn-outline" style="padding: 4px 10px; font-size:11px;" onclick="event.stopPropagation(); openCustomerModal('${c.customer_id}')">
            360 View →
          </button>
        </td>
      </tr>
    `).join("");

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="12" style="text-align:center; padding: 24px; color:var(--accent-rose);">Error loading customers: ${err.message}</td></tr>`;
  }
}

// 4. Open Customer 360 Drilldown Modal
async function openCustomerModal(customerId) {
  const modal = document.getElementById("customer-modal");
  const modalTitle = document.getElementById("modal-title");
  const modalCustId = document.getElementById("modal-cust-id");
  const modalBody = document.getElementById("modal-body-content");

  modal.classList.add("open");
  modalCustId.textContent = customerId;
  modalBody.innerHTML = `<p style="text-align:center; padding: 40px; color:var(--text-muted);">Fetching consolidated 360 data across accounts, loans, cards, transactions & CRM...</p>`;

  try {
    const res = await fetch(`/api/c360/customers/${customerId}`);
    const data = await res.json();
    const s = data.summary;

    modalTitle.textContent = `${s.full_name} (360° Profile)`;

    modalBody.innerHTML = `
      <div class="profile-hero">
        <div class="profile-avatar">${s.full_name.split(' ').map(n=>n[0]).join('')}</div>
        <div class="profile-info">
          <h2>${s.full_name}</h2>
          <p>${s.email} • ${s.phone} • ${s.city}, ${s.state}</p>
          <div class="profile-chips">
            <span class="tag-badge tag-info">${s.customer_segment}</span>
            <span class="tag-badge ${s.kyc_status === 'VERIFIED' ? 'tag-positive' : 'tag-warning'}">KYC: ${s.kyc_status}</span>
            <span class="tag-badge ${s.risk_tier === 'LOW' ? 'tag-positive' : 'tag-negative'}">Risk Tier: ${s.risk_tier}</span>
            <span class="tag-badge tag-warning">Credit Score: ${s.credit_score}</span>
          </div>
        </div>
      </div>

      <!-- Financial Snapshot Grid -->
      <div class="kpi-grid">
        <div class="kpi-card" style="padding:14px;">
          <div class="kpi-title">Total Relationship Value</div>
          <div class="kpi-value" style="font-size:20px; color:var(--accent-cyan);">$${Number(s.total_relationship_value).toLocaleString()}</div>
          <div class="kpi-footnote">LTV Score: <strong>${s.ltv_score}/100</strong></div>
        </div>
        <div class="kpi-card" style="padding:14px;">
          <div class="kpi-title">Deposit Balances</div>
          <div class="kpi-value" style="font-size:20px; color:var(--accent-emerald);">$${Number(s.total_deposit_balance).toLocaleString()}</div>
          <div class="kpi-footnote">${data.accounts.length} Active Accounts</div>
        </div>
        <div class="kpi-card" style="padding:14px;">
          <div class="kpi-title">Outstanding Loans</div>
          <div class="kpi-value" style="font-size:20px; color:var(--accent-indigo);">$${Number(s.total_loan_outstanding).toLocaleString()}</div>
          <div class="kpi-footnote">${s.has_overdue_loan ? `<span style="color:var(--accent-rose); font-weight:700;">${s.max_overdue_days} Days Past Due</span>` : 'Current / In Good Standing'}</div>
        </div>
        <div class="kpi-card" style="padding:14px;">
          <div class="kpi-title">Credit Card Limit</div>
          <div class="kpi-value" style="font-size:20px; color:var(--accent-purple);">$${Number(s.total_credit_limit).toLocaleString()}</div>
          <div class="kpi-footnote">Utilization: <strong>${s.credit_utilization_pct}%</strong></div>
        </div>
      </div>

      <!-- Accounts Section -->
      <div class="card">
        <div class="card-title" style="margin-bottom:12px;">Deposit Accounts (${data.accounts.length})</div>
        <div class="table-container">
          <table class="data-table">
            <thead><tr><th>Account ID</th><th>Status</th><th>Interest Rate</th><th>Current Balance</th><th>Available</th></tr></thead>
            <tbody>
              ${data.accounts.map(a => `
                <tr>
                  <td style="font-family:monospace; color:var(--accent-cyan);">${a.account_id}</td>
                  <td><span class="tag-badge ${a.status==='ACTIVE'?'tag-positive':'tag-warning'}">${a.status}</span></td>
                  <td>${a.interest_rate}%</td>
                  <td style="font-weight:700;">$${Number(a.current_balance).toLocaleString()}</td>
                  <td>$${Number(a.available_balance).toLocaleString()}</td>
                </tr>
              `).join("") || '<tr><td colspan="5">No deposit accounts</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Loans Section -->
      <div class="card">
        <div class="card-title" style="margin-bottom:12px;">Loan Portfolio Contracts (${data.loans.length})</div>
        <div class="table-container">
          <table class="data-table">
            <thead><tr><th>Loan ID</th><th>Principal</th><th>Outstanding</th><th>Monthly EMI</th><th>Overdue Days</th><th>Status</th></tr></thead>
            <tbody>
              ${data.loans.map(l => `
                <tr>
                  <td style="font-family:monospace; color:var(--accent-cyan);">${l.loan_id}</td>
                  <td>$${Number(l.principal_amount).toLocaleString()}</td>
                  <td style="font-weight:700;">$${Number(l.outstanding_balance).toLocaleString()}</td>
                  <td>$${Number(l.monthly_installment).toLocaleString()}</td>
                  <td style="color:${l.overdue_days > 0 ? 'var(--accent-rose)':'var(--text-muted)'}; font-weight:700;">${l.overdue_days}d</td>
                  <td><span class="tag-badge ${l.overdue_days > 0 ? 'tag-negative':'tag-positive'}">${l.delinquency_status}</span></td>
                </tr>
              `).join("") || '<tr><td colspan="6">No active loans</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent Transactions -->
      <div class="card">
        <div class="card-title" style="margin-bottom:12px;">Recent Payments & Transactions</div>
        <div class="table-container">
          <table class="data-table">
            <thead><tr><th>Txn ID</th><th>Type</th><th>Merchant / Category</th><th>Status</th><th>Amount</th></tr></thead>
            <tbody>
              ${data.recent_transactions.slice(0, 8).map(t => `
                <tr>
                  <td style="font-family:monospace; font-size:11px;">${t.transaction_id}</td>
                  <td><span class="tag-badge tag-info">${t.transaction_type}</span></td>
                  <td>${t.merchant_category || 'General'}</td>
                  <td><span class="tag-badge tag-positive">${t.status}</span></td>
                  <td style="font-weight:700; color:${t.transaction_type==='CREDIT'?'var(--accent-emerald)':'#fff'};">
                    ${t.transaction_type==='CREDIT'?'+':'-'}$${Number(t.amount).toFixed(2)}
                  </td>
                </tr>
              `).join("") || '<tr><td colspan="5">No recent transactions</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Omnichannel CRM Touchpoints -->
      <div class="card">
        <div class="card-title" style="margin-bottom:12px;">CRM Omnichannel Interactions & Sentiment</div>
        <div class="table-container">
          <table class="data-table">
            <thead><tr><th>Type</th><th>Sentiment</th><th>Score</th><th>Complaint</th><th>Status</th></tr></thead>
            <tbody>
              ${data.interactions.map(i => `
                <tr>
                  <td>${i.interaction_type}</td>
                  <td><span class="tag-badge ${i.sentiment==='POSITIVE'?'tag-positive':i.sentiment==='NEGATIVE'?'tag-negative':'tag-warning'}">${i.sentiment}</span></td>
                  <td style="font-weight:700;">${i.sentiment_score}</td>
                  <td>${i.is_complaint ? '<span class="tag-badge tag-negative">YES</span>':'No'}</td>
                  <td><span class="tag-badge tag-positive">${i.resolution_status}</span></td>
                </tr>
              `).join("") || '<tr><td colspan="5">No CRM interactions</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    `;

  } catch (err) {
    modalBody.innerHTML = `<p style="color:var(--accent-rose); padding:40px; text-align:center;">Failed to load customer profile: ${err.message}</p>`;
  }
}

function closeModal(event) {
  if (event && event.target && event.target !== document.getElementById("customer-modal") && event.target.className !== "modal-close") {
    return;
  }
  document.getElementById("customer-modal").classList.remove("open");
}

// 5. Business Questions Workbench
async function loadBusinessQuestion(qNumber) {
  document.querySelectorAll(".question-card-btn").forEach((btn, idx) => {
    if (idx + 1 === qNumber) btn.classList.add("active");
    else btn.classList.remove("active");
  });

  const titleEl = document.getElementById("bq-title");
  const subEl = document.getElementById("bq-subtitle");
  const badgeEl = document.getElementById("bq-badge-stat");
  const thead = document.getElementById("bq-table-head");
  const tbody = document.getElementById("bq-table-body");

  tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 24px;">Executing SQL Analytical Query...</td></tr>`;

  try {
    if (qNumber === 1) {
      titleEl.textContent = "Question 1: Which customers have multiple products?";
      subEl.textContent = "Customers holding across Deposits, Loans, and Credit Cards";
      const res = await fetch("/api/analytics/business-questions/multiple-products");
      const d = await res.json();
      badgeEl.textContent = `${d.total_qualifying_customers} Multi-Product Customers`;

      thead.innerHTML = `<tr><th>Customer ID</th><th>Full Name</th><th>Segment</th><th>Total Products</th><th>Deposit Accounts</th><th>Active Loans</th><th>Credit Cards</th><th>Relationship Assets</th></tr>`;
      tbody.innerHTML = d.customers.map(c => `
        <tr onclick="openCustomerModal('${c.customer_id}')">
          <td style="font-family:monospace; color:var(--accent-cyan); font-weight:700;">${c.customer_id}</td>
          <td>${c.full_name}</td>
          <td><span class="tag-badge tag-info">${c.customer_segment}</span></td>
          <td style="font-weight:800; color:var(--accent-emerald); text-align:center;">${c.total_products_held}</td>
          <td>${c.deposit_accounts}</td>
          <td>${c.active_loans}</td>
          <td>${c.credit_cards}</td>
          <td style="font-weight:700;">$${Number(c.total_relationship_value).toLocaleString()}</td>
        </tr>
      `).join("");

    } else if (qNumber === 2) {
      titleEl.textContent = "Question 2: Which customers are high-value?";
      subEl.textContent = "Customers ranked by Lifetime Value (LTV) and Assets Under Management";
      const res = await fetch("/api/analytics/business-questions/high-value");
      const d = await res.json();
      badgeEl.textContent = `${d.total_high_value_customers} VIP / High-Value Customers`;

      thead.innerHTML = `<tr><th>Customer ID</th><th>Full Name</th><th>Segment</th><th>Total Relationship Assets</th><th>Deposits</th><th>Loans</th><th>LTV Score</th><th>30d Txn Vol</th></tr>`;
      tbody.innerHTML = d.customers.map(c => `
        <tr onclick="openCustomerModal('${c.customer_id}')">
          <td style="font-family:monospace; color:var(--accent-cyan); font-weight:700;">${c.customer_id}</td>
          <td>${c.full_name}</td>
          <td><span class="tag-badge tag-info">${c.customer_segment}</span></td>
          <td style="font-weight:800; color:var(--accent-cyan);">$${Number(c.total_relationship_value).toLocaleString()}</td>
          <td style="color:var(--accent-emerald);">$${Number(c.total_deposit_balance).toLocaleString()}</td>
          <td>$${Number(c.total_loan_outstanding).toLocaleString()}</td>
          <td><span class="tag-badge tag-positive">${c.ltv_score} / 100</span></td>
          <td>$${Number(c.txn_volume_30d).toLocaleString()}</td>
        </tr>
      `).join("");

    } else if (qNumber === 3) {
      titleEl.textContent = "Question 3: Which customers have overdue loans?";
      subEl.textContent = "Delinquency tracking across 30, 60, 90+ DPD (Non-Performing Loans)";
      const res = await fetch("/api/analytics/business-questions/overdue-loans");
      const d = await res.json();
      badgeEl.textContent = `${d.total_overdue_loans} Delinquent Loans`;

      thead.innerHTML = `<tr><th>Customer ID</th><th>Full Name</th><th>Phone</th><th>Loan ID</th><th>Outstanding</th><th>Overdue Days</th><th>Overdue Amount</th><th>Delinquency Status</th></tr>`;
      tbody.innerHTML = d.loans.map(l => `
        <tr onclick="openCustomerModal('${l.customer_id}')">
          <td style="font-family:monospace; color:var(--accent-cyan); font-weight:700;">${l.customer_id}</td>
          <td>${l.full_name}</td>
          <td>${l.phone}</td>
          <td style="font-family:monospace;">${l.loan_id}</td>
          <td>$${Number(l.outstanding_balance).toLocaleString()}</td>
          <td style="color:var(--accent-rose); font-weight:800;">${l.overdue_days} Days</td>
          <td style="color:var(--accent-rose); font-weight:700;">$${Number(l.overdue_amount).toLocaleString()}</td>
          <td><span class="tag-badge tag-negative">${l.delinquency_status}</span></td>
        </tr>
      `).join("");

    } else if (qNumber === 4) {
      titleEl.textContent = "Question 4: What is the monthly transaction volume?";
      subEl.textContent = "Monthly payment throughput, ticket sizes, and debit vs credit splits";
      const res = await fetch("/api/analytics/business-questions/monthly-transactions");
      const d = await res.json();
      badgeEl.textContent = `${d.monthly_trends.length} Months Tracked`;

      thead.innerHTML = `<tr><th>Period</th><th>Month</th><th>Transactions</th><th>Total Volume</th><th>Avg Ticket Size</th><th>Debit Volume</th><th>Credit Volume</th><th>Fraud Flagged</th></tr>`;
      tbody.innerHTML = d.monthly_trends.map(m => `
        <tr>
          <td style="font-weight:700; color:var(--accent-cyan);">${m.period}</td>
          <td>${m.month_name} ${m.year}</td>
          <td style="font-weight:700;">${Number(m.transaction_count).toLocaleString()}</td>
          <td style="font-weight:800; color:var(--accent-emerald);">$${Number(m.total_volume).toLocaleString()}</td>
          <td>$${Number(m.average_ticket_size).toFixed(2)}</td>
          <td>$${Number(m.debit_volume).toLocaleString()}</td>
          <td>$${Number(m.credit_volume).toLocaleString()}</td>
          <td><span class="tag-badge ${m.fraud_transactions_flagged>0?'tag-warning':'tag-positive'}">${m.fraud_transactions_flagged}</span></td>
        </tr>
      `).join("");

    } else if (qNumber === 5) {
      titleEl.textContent = "Question 5: Which customers have declining engagement?";
      subEl.textContent = "Early churn warning signals: Negative sentiment, unresolved disputes, zero 30d activity";
      const res = await fetch("/api/analytics/business-questions/declining-engagement");
      const d = await res.json();
      badgeEl.textContent = `${d.total_at_risk_customers} At-Risk Customers`;

      thead.innerHTML = `<tr><th>Customer ID</th><th>Full Name</th><th>Segment</th><th>Relationship Assets</th><th>Engagement Status</th><th>Avg Sentiment</th><th>Unresolved Complaints</th><th>30d Txn Count</th></tr>`;
      tbody.innerHTML = d.customers.map(c => `
        <tr onclick="openCustomerModal('${c.customer_id}')">
          <td style="font-family:monospace; color:var(--accent-cyan); font-weight:700;">${c.customer_id}</td>
          <td>${c.full_name}</td>
          <td><span class="tag-badge tag-info">${c.customer_segment}</span></td>
          <td>$${Number(c.total_relationship_value).toLocaleString()}</td>
          <td><span class="tag-badge ${c.engagement_status==='DECLINING'?'tag-negative':'tag-warning'}">${c.engagement_status}</span></td>
          <td style="color:${c.avg_sentiment_score < 0 ? 'var(--accent-rose)':'var(--accent-emerald)'}; font-weight:700;">${c.avg_sentiment_score}</td>
          <td style="text-align:center;">${c.unresolved_complaints > 0 ? `<span class="tag-badge tag-negative">${c.unresolved_complaints}</span>` : '0'}</td>
          <td>${c.txn_count_30d}</td>
        </tr>
      `).join("");

    } else if (qNumber === 6) {
      titleEl.textContent = "Question 6: Which customer segments have the highest risk?";
      subEl.textContent = "Cross-segment risk matrix combining credit scores, AML risk indices, and overdue rates";
      const res = await fetch("/api/analytics/business-questions/high-risk-segments");
      const d = await res.json();
      badgeEl.textContent = `${d.segments.length} Portfolio Segments Evaluated`;

      thead.innerHTML = `<tr><th>Customer Segment</th><th>Customers</th><th>Avg Credit Score</th><th>Avg AML Risk</th><th>Composite Risk</th><th>Delinquency Rate</th><th>Total Overdue Exposure</th><th>Risk Rating</th></tr>`;
      tbody.innerHTML = d.segments.map(s => `
        <tr>
          <td style="font-weight:700; color:#fff;">${s.customer_segment}</td>
          <td>${s.total_customers}</td>
          <td style="font-weight:700;">${s.avg_credit_score}</td>
          <td>${s.avg_aml_risk_score}</td>
          <td style="font-weight:800; color:var(--accent-amber);">${s.avg_composite_risk_score}</td>
          <td style="color:${s.delinquency_rate_pct>10?'var(--accent-rose)':'var(--text-main)'}; font-weight:700;">${s.delinquency_rate_pct}%</td>
          <td style="color:var(--accent-rose); font-weight:700;">$${Number(s.total_overdue_amount).toLocaleString()}</td>
          <td><span class="tag-badge ${s.risk_rating==='HIGH RISK'?'tag-negative':s.risk_rating==='MODERATE RISK'?'tag-warning':'tag-positive'}">${s.risk_rating}</span></td>
        </tr>
      `).join("");
    }

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 24px; color:var(--accent-rose);">Error executing analytical question: ${err.message}</td></tr>`;
  }
}

// 6. Data Quality Report
async function loadDataQualityReport() {
  const tbody = document.getElementById("dq-table-body");
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px;">Running 15 Automated Data Quality Rule Checks...</td></tr>`;

  try {
    const res = await fetch("/api/governance/quality");
    const d = await res.json();

    document.getElementById("dq-overall-status").textContent = d.overall_status;
    document.getElementById("dq-pass-rate").textContent = `${d.pass_rate_pct}%`;
    document.getElementById("dq-pass-counts").textContent = `${d.passed_rules} of ${d.total_rules} Passed`;
    document.getElementById("dq-duration").textContent = `${d.duration_seconds}s`;

    tbody.innerHTML = d.rule_details.map(r => `
      <tr>
        <td style="font-family:monospace; color:var(--accent-cyan); font-weight:700;">${r.rule_id}</td>
        <td style="font-weight:600;">${r.name}</td>
        <td><code>${r.table_name}</code></td>
        <td><span class="tag-badge tag-info">${r.rule_type}</span></td>
        <td><span class="tag-badge ${r.severity==='CRITICAL'?'tag-negative':'tag-warning'}">${r.severity}</span></td>
        <td><span class="tag-badge ${r.status==='PASSED'?'tag-positive':'tag-negative'}">${r.status}</span></td>
        <td style="font-weight:700; color:${r.violations_detected > 0 ? 'var(--accent-rose)':'var(--accent-emerald)'}; text-align:center;">
          ${r.violations_detected}
        </td>
      </tr>
    `).join("");

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color:var(--accent-rose);">Error loading Data Quality Scorecard: ${err.message}</td></tr>`;
  }
}

// 7. Trigger Pipeline Execution
async function triggerPipeline() {
  const btn = document.getElementById("btn-trigger-etl");
  const oldText = btn.innerHTML;
  btn.innerHTML = `<span>Running Pipeline...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch("/api/governance/trigger-pipeline", { method: "POST" });
    const data = await res.json();
    alert(`ETL Pipeline finished successfully in ${data.duration_seconds}s! Processed ${data.records_processed.customers} customers & ${data.records_processed.transactions} transactions.`);
    
    // Refresh all views
    loadExecutiveKPIs();
    loadOverviewCharts();
    loadCustomers();
    loadDataQualityReport();
  } catch (err) {
    alert(`ETL Pipeline failed: ${err.message}`);
  } finally {
    btn.innerHTML = oldText;
    btn.disabled = false;
  }
}

// ============================================================================
// 8. BI Integration Hub — Power BI & Tableau
// ============================================================================

function switchBITool(tool) {
  document.querySelectorAll(".bi-tab-btn").forEach(btn => btn.classList.remove("active"));
  document.querySelectorAll(".bi-panel").forEach(panel => panel.classList.remove("active"));

  document.getElementById(`bi-tab-${tool}`).classList.add("active");
  document.getElementById(`bi-panel-${tool}`).classList.add("active");
}

async function loadBISummary() {
  try {
    const res = await fetch("/api/exports/bi-summary");
    const data = await res.json();
    const dw = data.data_warehouse;

    document.getElementById("bi-total-c360").textContent = Number(dw.total_c360_records).toLocaleString();
    document.getElementById("bi-total-txns").textContent = Number(dw.total_transactions).toLocaleString();
    document.getElementById("bi-total-loans").textContent = Number(dw.total_loan_records).toLocaleString();
    document.getElementById("bi-total-dims").textContent = Number(dw.total_dimension_records).toLocaleString();
  } catch (err) {
    console.error("Failed to load BI summary:", err);
  }
}

async function loadPowerBIModel() {
  try {
    const res = await fetch("/api/exports/powerbi/semantic-model");
    const data = await res.json();

    // Render DAX Measures
    const measuresContainer = document.getElementById("powerbi-dax-measures");
    if (measuresContainer && data.dax_measures) {
      measuresContainer.innerHTML = data.dax_measures.map(m => `
        <div class="bi-measure-card">
          <div class="bi-measure-header">
            <span class="bi-measure-name">${m.name}</span>
            <span class="tag-badge tag-warning">${m.category}</span>
          </div>
          <div class="bi-measure-desc">${m.description}</div>
          <pre class="bi-measure-code">${escapeHtml(m.expression)}</pre>
        </div>
      `).join("");
    }

    // Render Relationships
    const relBody = document.getElementById("powerbi-relationships-body");
    if (relBody && data.relationships) {
      relBody.innerHTML = data.relationships.map(r => `
        <tr>
          <td style="font-weight: 700; color: var(--accent-cyan);"><code>${r.from_table}</code></td>
          <td><code>${r.from_column}</code></td>
          <td style="font-weight: 700; color: var(--accent-purple);"><code>${r.to_table}</code></td>
          <td><code>${r.to_column}</code></td>
          <td><span class="tag-badge tag-info">${r.cardinality}</span></td>
          <td><span class="tag-badge tag-positive">${r.cross_filter}</span></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Failed to load Power BI model:", err);
  }
}

async function loadTableauModel() {
  try {
    const res = await fetch("/api/exports/tableau/semantic-model");
    const data = await res.json();

    // Render Calculated Fields
    const fieldsContainer = document.getElementById("tableau-calc-fields");
    if (fieldsContainer && data.calculated_fields) {
      fieldsContainer.innerHTML = data.calculated_fields.map(f => `
        <div class="bi-measure-card" style="--measure-accent: #E97627;">
          <div class="bi-measure-header">
            <span class="bi-measure-name">${f.name}</span>
            <span class="tag-badge" style="background: rgba(233, 118, 39, 0.2); color: #E97627;">${f.category}</span>
          </div>
          <div class="bi-measure-desc">${f.description}</div>
          <pre class="bi-measure-code" style="border-color: rgba(233, 118, 39, 0.2);">${escapeHtml(f.formula)}</pre>
        </div>
      `).join("");
    }

    // Render Recommended Dashboards
    const dashContainer = document.getElementById("tableau-dashboards");
    if (dashContainer && data.recommended_dashboards) {
      dashContainer.innerHTML = data.recommended_dashboards.map(d => `
        <div class="question-card-btn" style="cursor: default; border-color: rgba(233, 118, 39, 0.3); background: rgba(233, 118, 39, 0.05);">
          <h4 style="color: #E97627;">${d.name}</h4>
          <p>${d.worksheets.join(" • ")}</p>
        </div>
      `).join("");
    }

    // Render Relationships
    const relBody = document.getElementById("tableau-relationships-body");
    if (relBody && data.tables) {
      const relationships = [
        { dim: "dim_customer", key: "customer_key", fact: "fact_transactions", fk: "customer_key", type: "Inner" },
        { dim: "dim_customer", key: "customer_key", fact: "fact_daily_account_snapshot", fk: "customer_key", type: "Inner" },
        { dim: "dim_customer", key: "customer_key", fact: "fact_loan_performance", fk: "customer_key", type: "Inner" },
        { dim: "dim_customer", key: "customer_key", fact: "fact_customer_interactions", fk: "customer_key", type: "Inner" },
        { dim: "dim_customer", key: "customer_key", fact: "c360_customer_mart", fk: "customer_key", type: "Inner" },
        { dim: "dim_date", key: "date_key", fact: "fact_transactions", fk: "date_key", type: "Inner" },
        { dim: "dim_date", key: "date_key", fact: "fact_daily_account_snapshot", fk: "date_key", type: "Inner" },
        { dim: "dim_date", key: "date_key", fact: "fact_loan_performance", fk: "date_key", type: "Inner" },
        { dim: "dim_product", key: "product_key", fact: "fact_transactions", fk: "product_key", type: "Inner" },
        { dim: "dim_channel", key: "channel_key", fact: "fact_transactions", fk: "channel_key", type: "Inner" },
      ];
      relBody.innerHTML = relationships.map(r => `
        <tr>
          <td style="font-weight: 700; color: #E97627;"><code>${r.dim}</code></td>
          <td><code>${r.key}</code></td>
          <td style="font-weight: 700; color: var(--accent-purple);"><code>${r.fact}</code></td>
          <td><code>${r.fk}</code></td>
          <td><span class="tag-badge tag-positive">${r.type}</span></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Failed to load Tableau model:", err);
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Load BI Hub data on page load (deferred)
document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    loadBISummary();
    loadPowerBIModel();
    loadTableauModel();
  }, 500);
});
