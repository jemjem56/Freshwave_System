/* ------------------------
ORDER DETAIL - VIEW RECEIPT
--------------------------- */
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
    const prev = document.title;
    document.title = 'Receipt-Order-{{ order.order_number }}-{{ order.customer.name|slugify }}';
    window.print();
    setTimeout(function () {
        document.title = prev;
    }, 300);
}

document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('receiptModal');
    if (!modal) return;

    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeReceipt();
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeReceipt();
    });
});