/* -------------------------------------------------------------
    SECTION 1 — LIGHT AND DARK THEME
------------------------------------------------------------- */
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    localStorage.setItem('fw-theme', next);
}

(function () {
    const saved = localStorage.getItem('fw-theme') || 'dark';
    applyTheme(saved);
})();

/* -------------------------------------------------------------
    SECTION 2 — NOTIFICATION BELL
------------------------------------------------------------- */
// ── Auto-dismiss Django alert messages ───────────────────────
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
        if (window.bootstrap && bootstrap.Alert) {
            new bootstrap.Alert(a).close();
        } else {
            a.remove();
        }
    });
}, 4000);

// ── Notification bell controller ─────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    const wrap    = document.getElementById('notifDropdownWrap');
    const bellBtn = document.getElementById('notifBellBtn');

    // Guard: if bell markup not present on this page, stop here
    if (!wrap || !bellBtn) return;

    // Open / close on bell click
    bellBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        const isOpen = wrap.classList.toggle('notif-open');
        bellBtn.setAttribute('aria-expanded', String(isOpen));
    });

    // Close when clicking anywhere outside the panel
    document.addEventListener('click', function (e) {
        if (!wrap.contains(e.target)) {
            wrap.classList.remove('notif-open');
            bellBtn.setAttribute('aria-expanded', 'false');
        }
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && wrap.classList.contains('notif-open')) {
            wrap.classList.remove('notif-open');
            bellBtn.setAttribute('aria-expanded', 'false');
            bellBtn.focus();
        }
    });

    // ── Tab switching ─────────────────────────────────────────
    // Reads data-tab-target on each .notif-tab button
    wrap.addEventListener('click', function (e) {
        const tab = e.target.closest('.notif-tab');
        if (!tab || !tab.dataset.tabTarget) return;

        wrap.querySelectorAll('.notif-tab').forEach(t => t.classList.remove('active'));
        wrap.querySelectorAll('.notif-scroll-area').forEach(p => p.classList.add('notif-tab-panel-hidden'));

        tab.classList.add('active');
        const panel = document.getElementById(tab.dataset.tabTarget);
        if (panel) panel.classList.remove('notif-tab-panel-hidden');
    });

    // ── Confirm-before-submit for Delete all ─────────────────
    // Uses data-confirm="message" attribute on the button
    wrap.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-confirm]');
        if (!btn) return;
        if (!window.confirm(btn.dataset.confirm)) {
            e.preventDefault();
        }
    });

});

// ── Close sidebar on outside click (mobile) ──────────────────
document.addEventListener('click', function (e) {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;
    if (
        window.innerWidth < 768 &&
        !sidebar.contains(e.target) &&
        !e.target.closest('.mobile-toggle')
    ) {
        sidebar.classList.remove('show');
    }
});

/* -------------------------------------------------------------
    SECTION 3 — ORDER DETAIL
------------------------------------------------------------- */

function openReceipt() {
    const modal = document.getElementById('receiptModal');
    if (!modal) return;
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeReceipt() {
    const modal = document.getElementById('receiptModal');
    if (!modal) return;
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

function printReceipt() {
    window.print();
}

function downloadReceipt() {
    window.print();
}

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('receiptModal');

    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) closeReceipt();
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeReceipt();
        });
    }

/* ---------------------------------------------------------
    STEP 3.1: ORDER FORM SAFE BINDINGS
--------------------------------------------------------- */
const weightInput = document.querySelector('[name="weight_kg"]');
const orderForm = document.getElementById('orderForm');
const submitBtn = document.getElementById('submitBtn');
const totalDisplay = document.getElementById('totalDisplay');
const summaryItems = document.getElementById('summaryItems');
const serviceCheckboxes = document.querySelectorAll('.service-checkbox');
const weightHelpText = document.getElementById('weightHelpText');

let packageSelected = false;
let packageId = null;
/* -------------------
DETECT PACKAGE SERVICE
-------------------- */
serviceCheckboxes.forEach(cb => {
    if (cb.dataset.package === 'true') {
        packageId = cb.dataset.id;
    }
});

/* --------------
GET WEIGHT
----------------- */
function getWeight() {
    if (!weightInput) return 1;
    const val = parseFloat(weightInput.value);
    return isNaN(val) || val <= 0 ? 1 : val;    
}

/* --------------
CARD VISUAL STATE
----------------- */
function setCardLocked(card, locked) {
    if (!card) return;

    if (locked) {
        card.style.opacity = '0.45';
        card.style.pointerEvents = 'none';
        card.style.cursor = 'not-allowed';
    } else {
        card.style.opacity = '1';
        card.style.pointerEvents = 'auto';
        card.style.cursor = 'pointer';
    }    
} 
/* --------------
PACKAGE MODE
----------------- */
function enablePackageMode() {
packageSelected = true;

serviceCheckboxes.forEach(cb => {
    if (cb.dataset.id !== packageId) {
        cb.checked = false;
        cb.disabled = true;

        const card = document.getElementById('card_' + cb.dataset.id);
            if (card) {
                card.classList.remove('selected');
                setCardLocked(card, true);
            }
        }
    });
    if (weightInput) {
        weightInput.value = '5.0';
        weightInput.max = 5;
        weightInput.min = 5;
        weightInput.disabled = true;
    }

    if (weightHelpText) {
        weightHelpText.innerHTML =
            '<span style="color:var(--warning);">Promo package is up to 5kg only</span>';
    }
}
function disablePackageMode() {
    packageSelected = false;

    serviceCheckboxes.forEach(cb => {
        if (cb.dataset.id !== packageId) {
            cb.disabled = false;

            const card = document.getElementById('card_' + cb.dataset.id);

            setCardLocked(card, false);
        }
    });
    if (weightInput) {
        weightInput.disabled = false;
        weightInput.removeAttribute('max');
        weightInput.removeAttribute('min');
        weightInput.value = '';
    }

    if (weightHelpText) {
        weightHelpText.textContent =
            'Used for per-kg pricing calculation';
    }
}
/* --------------
TOGGLE SERVICE
----------------- */
window.toggleService = function (id) {
    const cb = document.getElementById('svc_' + id);
    if (!cb) return;
    cb.checked = !cb.checked;
    cb.dispatchEvent(new Event('change'));
};
/* --------------
UPDATE SUMMARY
----------------- */
function updateSummary() {
    if (!totalDisplay || !summaryItems || !serviceCheckboxes.length) {
        return;
    }
    const weight = getWeight();
    let total = 0;
    let items = [];

    serviceCheckboxes.forEach(cb => {
        const card = document.getElementById('card_' + cb.dataset.id);
        const price = parseFloat(cb.dataset.price || 0);
        const isPackage = cb.dataset.package === 'true';

            if (cb.checked) {
                if (card) { 
                    card.classList.add('selected'); 
                }
                let subtotal;
                // Package price should NOT multiply by weight
                if (isPackage) {
                    subtotal = price;
                } else {
                    subtotal = price * weight;
                }
                total += subtotal;

                items.push(`
                    <div style="display:grid;grid-template-columns: 1fr 120px;align-items:center;margin-bottom:8px;width:100%;">
                        <span style="color:var(--text);">${cb.dataset.name} ${isPackage ? '' : ` x ${weight}kg`}</span>
                        <span style="font-weight:700;color:var(--accent);text-align:right;">₱${subtotal.toFixed(2)}</span>
                    </div>
                `);
            } else {
                if (card) card.classList.remove('selected');
            }
        });

        totalDisplay.textContent = '₱' + total.toFixed(2);
        summaryItems.innerHTML = items.length
            ? items.join('')
            : '<span style="color:var(--text-muted);">Select services to see summary...</span>';
    }
/* --------------
CHECKBOX EVENTS
----------------- */
serviceCheckboxes.forEach(cb => {
    cb.addEventListener('change', function () {

        const isPackage = this.dataset.package === 'true';
        // Package selected
        if (isPackage && this.checked) {
            enablePackageMode();
        } else if (isPackage && !this.checked) {
            disablePackageMode();
        } else if (!isPackage && packageSelected) {
            this.checked = false;
            return;
        }
        updateSummary();
    });
});
/* --------------
WEIGHT INPUT
----------------- */
if (weightInput) {
    weightInput.addEventListener('input', updateSummary);
}
/* --------------
FORM VALIDATION
----------------- */
    if (orderForm) {
        orderForm.addEventListener('submit', function (e) {
            const anyChecked = document.querySelectorAll('.service-checkbox:checked').length > 0;
            const customerInput = document.querySelector('[name="customer"]');
            const customer = customerInput ? customerInput.value : '';
            const packageCheckbox = document.querySelector('.service-checkbox[data-package="true"]');

            if (packageCheckbox && packageCheckbox.checked && parseFloat(getWeight()) > 5) {
                e.preventDefault();
                alert('Promo package is limited to a maximum of 5kg only.');
                return;
            }

            if (!customer) {
                e.preventDefault();
                alert('Please select a customer.');
                return;
            }

            if (!anyChecked) {
                e.preventDefault();
                alert('Please select at least one service.');
                return;
            }

            if (submitBtn) {
                submitBtn.innerHTML = '<i class="bi bi-hourglass me-1"></i>Creating...';
                submitBtn.disabled = true;
            }
        });

        updateSummary();
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("customerSearchInput");
    const suggestionsBox = document.getElementById("customerSearchSuggestions");
    const dataScript = document.getElementById("customer-names-data");

    if (!searchInput || !suggestionsBox || !dataScript) {
        console.log("Missing element:", {
            searchInput,
            suggestionsBox,
            dataScript
        });
        return;
    }

    let customers = [];
    let activeIndex = -1;

    try {
        customers = JSON.parse(dataScript.textContent);
        console.log("Loaded customers:", customers);
    } catch (error) {
        console.error("Failed to parse customer names JSON:", error);
        return;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function highlightMatch(text, query) {
        if (!query) return escapeHtml(text);

        const escapedText = escapeHtml(text);
        const regex = new RegExp("(" + escapeRegExp(query) + ")", "ig");
        return escapedText.replace(regex, "<strong>$1</strong>");
    }

    function hideSuggestions() {
        suggestionsBox.classList.add("d-none");
        suggestionsBox.innerHTML = "";
        activeIndex = -1;
    }

    function showSuggestions(matches, query) {
        suggestionsBox.innerHTML = "";

        if (!matches.length) {
            hideSuggestions();
            return;
        }

        matches.forEach(function (name, index) {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.dataset.index = index;
            item.dataset.value = name;
            item.innerHTML = highlightMatch(name, query);

            item.addEventListener("mousedown", function (event) {
                event.preventDefault();
                searchInput.value = name;
                hideSuggestions();
            });

            suggestionsBox.appendChild(item);
        });

        suggestionsBox.classList.remove("d-none");
    }

    function updateSuggestions() {
        const value = searchInput.value.trim().toLowerCase();

        if (value.length < 1) {
            hideSuggestions();
            return;
        }

        const matches = customers
            .filter(function (name) {
                return String(name).toLowerCase().includes(value);
            })
            .slice(0, 8);

        showSuggestions(matches, value);
    }

    function setActiveItem(items) {
        items.forEach(function (item) {
            item.classList.remove("active");
        });

        if (activeIndex >= 0 && activeIndex < items.length) {
            items[activeIndex].classList.add("active");
        }
    }

    searchInput.addEventListener("input", updateSuggestions);

    searchInput.addEventListener("keydown", function (event) {
        const items = suggestionsBox.querySelectorAll(".autocomplete-item");

        if (suggestionsBox.classList.contains("d-none") || !items.length) {
            return;
        }

        if (event.key === "ArrowDown") {
            event.preventDefault();
            activeIndex = (activeIndex + 1) % items.length;
            setActiveItem(items);
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            activeIndex = (activeIndex - 1 + items.length) % items.length;
            setActiveItem(items);
        } else if (event.key === "Enter") {
            if (activeIndex >= 0 && activeIndex < items.length) {
                event.preventDefault();
                searchInput.value = items[activeIndex].dataset.value;
                hideSuggestions();
            }
        } else if (event.key === "Escape") {
            hideSuggestions();
        }
    });

    document.addEventListener("click", function (event) {
        if (!searchInput.closest(".search-box").contains(event.target)) {
            hideSuggestions();
        }
    });

    searchInput.addEventListener("focus", function () {
        if (searchInput.value.trim().length >= 1) {
            updateSuggestions();
        }
    });
});

/* ---------------------------------------------------------
    STEP 4.1: ORDER SEARCHING - CUSTOM AUTOCOMPLETE
--------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("orderSearchInput");
    const suggestionsBox = document.getElementById("orderSearchSuggestions");
    const dataScript = document.getElementById("order-customer-names-data");

    if (!searchInput || !suggestionsBox || !dataScript) {
        return;
    }

    let customers = [];
    let activeIndex = -1;

    try {
        customers = JSON.parse(dataScript.textContent);
    } catch (error) {
        console.error("Failed to parse order customer names JSON:", error);
        return;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function highlightMatch(text, query) {
        if (!query) return escapeHtml(text);

        const escapedText = escapeHtml(text);
        const regex = new RegExp("(" + escapeRegExp(query) + ")", "ig");
        return escapedText.replace(regex, "<strong>$1</strong>");
    }

    function hideSuggestions() {
        suggestionsBox.classList.add("d-none");
        suggestionsBox.innerHTML = "";
        activeIndex = -1;
    }

    function showSuggestions(matches, query) {
        suggestionsBox.innerHTML = "";

        if (!matches.length) {
            hideSuggestions();
            return;
        }

        matches.forEach(function (name, index) {
            const item = document.createElement("div");
            item.className = "autocomplete-item";
            item.dataset.index = index;
            item.dataset.value = name;
            item.innerHTML = highlightMatch(name, query);

            item.addEventListener("mousedown", function (event) {
                event.preventDefault();
                searchInput.value = name;
                hideSuggestions();
            });

            suggestionsBox.appendChild(item);
        });

        suggestionsBox.classList.remove("d-none");
    }

    function updateSuggestions() {
        const value = searchInput.value.trim().toLowerCase();

        if (value.length < 1) {
            hideSuggestions();
            return;
        }

        const matches = customers
            .filter(function (name) {
                return String(name).toLowerCase().includes(value);
            })
            .slice(0, 8);

        showSuggestions(matches, value);
    }

    function setActiveItem(items) {
        items.forEach(function (item) {
            item.classList.remove("active");
        });

        if (activeIndex >= 0 && activeIndex < items.length) {
            items[activeIndex].classList.add("active");
        }
    }

    searchInput.addEventListener("input", updateSuggestions);

    searchInput.addEventListener("keydown", function (event) {
        const items = suggestionsBox.querySelectorAll(".autocomplete-item");

        if (suggestionsBox.classList.contains("d-none") || !items.length) {
            return;
        }

        if (event.key === "ArrowDown") {
            event.preventDefault();
            activeIndex = (activeIndex + 1) % items.length;
            setActiveItem(items);
        } else if (event.key === "ArrowUp") {
            event.preventDefault();
            activeIndex = (activeIndex - 1 + items.length) % items.length;
            setActiveItem(items);
        } else if (event.key === "Enter") {
            if (activeIndex >= 0 && activeIndex < items.length) {
                event.preventDefault();
                searchInput.value = items[activeIndex].dataset.value;
                hideSuggestions();
            }
        } else if (event.key === "Escape") {
            hideSuggestions();
        }
    });

    document.addEventListener("click", function (event) {
        if (!searchInput.closest(".search-box").contains(event.target)) {
            hideSuggestions();
        }
    });

    searchInput.addEventListener("focus", function () {
        if (searchInput.value.trim().length >= 1) {
            updateSuggestions();
        }
    });
});

/* -------------------------------------------------------------
    SECTION 5: Base Deleted
    Notifications / Customers / Orders
   ------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", function () {
    const confirmDeleteModal = document.getElementById("confirmDeleteModal");

    if (!confirmDeleteModal) return;

    confirmDeleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;

        if (!button) return;

        const deleteUrl = button.getAttribute("data-delete-url");
        const deleteType = button.getAttribute("data-delete-type") || "item";
        const deleteName = button.getAttribute("data-delete-name") || "this item";
        const deleteAll = button.getAttribute("data-delete-all") === "true";

        const modalTitle = document.getElementById("confirmDeleteModalLabel");
        const modalMessage = document.getElementById("confirmDeleteMessage");
        const modalForm = document.getElementById("confirmDeleteForm");

        modalForm.action = deleteUrl;

        if (deleteAll) {
            modalTitle.textContent = `Delete ${deleteType}?`;

            modalMessage.innerHTML = `
                You're about to <strong class="delete-name">${deleteName}</strong>.<br>
            `;
        } else {
            modalTitle.textContent = `Delete ${deleteType}?`;

            modalMessage.innerHTML = `
                You're about to delete
                <strong class="delete-name">${deleteName}</strong>.<br>
                This action <strong class="delete-name">cannot be undone</strong>.
            `;
        }
    });
});
/* -------------------------------------------------------------
    SECTION 6: CUSTOM DROPDOWN PANEL
   ------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    const dropdown = document.querySelector('.status-dropdown');
    const toggle = document.getElementById('statusToggle');
    const menu = document.getElementById('statusMenu');
    const input = document.getElementById('statusInput');
    const label = document.getElementById('selectedStatus');

    // Stop if elements not found
    if (!dropdown || !toggle || !menu) return;

    // Open / close
    toggle.addEventListener('click', (e) => {
        e.stopPropagation();

        dropdown.classList.toggle('open');
    });

    // Select item
    menu.querySelectorAll('button').forEach((btn) => {
        btn.addEventListener('click', () => {

            input.value = btn.dataset.value;

            label.textContent =
                btn.textContent.trim();

            dropdown.classList.remove('open');

            toggle.closest('form').submit();
        });
    });

    // Close outside
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('open');
        }
    });

});