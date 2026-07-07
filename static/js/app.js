document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        serialInput: document.getElementById('serial-number'),
        previewBtn: document.getElementById('btn-preview'),
        generateBtn: document.getElementById('btn-generate'),
        generateAllBtn: document.getElementById('btn-generate-all'),
        generateRangeBtn: document.getElementById('btn-generate-range'),
        generateCustomBtn: document.getElementById('btn-generate-custom'),
        rangeStart: document.getElementById('range-start'),
        rangeEnd: document.getElementById('range-end'),
        customSerials: document.getElementById('custom-serials'),
        statusMessage: document.getElementById('status-message'),
        statusIcon: document.getElementById('status-icon'),
        statusText: document.getElementById('status-text'),
        modalOverlay: document.getElementById('preview-modal'),
        modalBody: document.getElementById('modal-body'),
        modalClose: document.getElementById('modal-close'),
        spinnerOverlay: document.getElementById('spinner-overlay'),
        spinnerText: document.getElementById('spinner-text'),
        downloadArea: document.getElementById('download-area'),
        downloadLink: document.getElementById('download-link'),
        statusBadge: document.getElementById('status-badge'),
        allCount: document.getElementById('all-count'),
        modeTabs: document.querySelectorAll('.mode-tab'),
        modePanels: document.querySelectorAll('.mode-panel'),
    };

    let totalApplicants = 0;

    function showStatus(type, icon, message) {
        elements.statusMessage.className = 'status-message show ' + type;
        elements.statusIcon.className = 'status-icon ' + icon;
        elements.statusText.textContent = message;
    }

    function hideStatus() {
        elements.statusMessage.className = 'status-message';
    }

    function showSpinner(text) {
        elements.spinnerText.textContent = text || 'Processing...';
        elements.spinnerOverlay.classList.add('show');
    }

    function hideSpinner() {
        elements.spinnerOverlay.classList.remove('show');
    }

    function showDownload(filename) {
        elements.downloadLink.href = '/download/' + encodeURIComponent(filename);
        elements.downloadArea.classList.add('show');
    }

    function hideDownload() {
        elements.downloadArea.classList.remove('show');
    }

    function updateStatusBadge(loaded, total) {
        elements.statusBadge.classList.toggle('loaded', loaded);
        var text = elements.statusBadge.querySelector('.status-text');
        if (loaded) {
            text.textContent = total + ' applicant' + (total !== 1 ? 's' : '') + ' loaded';
            if (elements.allCount) elements.allCount.textContent = total;
            totalApplicants = total;
        } else {
            text.textContent = 'No data loaded';
        }
    }

    function switchMode(mode) {
        elements.modeTabs.forEach(function (t) {
            t.classList.toggle('active', t.dataset.mode === mode);
        });
        elements.modePanels.forEach(function (p) {
            p.classList.toggle('active', p.id === 'mode-' + mode);
        });
        hideStatus();
        hideDownload();
    }

    elements.modeTabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            switchMode(this.dataset.mode);
        });
    });

    function fetchExcel() {
        showSpinner('Fetching applicant data...');
        fetch('/fetch', { method: 'POST' })
            .then(function (r) { return r.json().then(function (d) { return { status: r.status, data: d }; }); })
            .then(function (r) {
                hideSpinner();
                if (r.data.success) {
                    updateStatusBadge(true, r.data.total);
                } else {
                    updateStatusBadge(false, 0);
                    showStatus('error', 'fas fa-exclamation-circle', r.data.message);
                }
            })
            .catch(function () {
                hideSpinner();
                updateStatusBadge(false, 0);
                showStatus('error', 'fas fa-exclamation-circle', 'Failed to fetch applicant data.');
            });
    }

    fetchExcel();

    elements.previewBtn.addEventListener('click', function () {
        var serial = elements.serialInput.value.trim();
        if (!serial) { showStatus('warning', 'fas fa-exclamation-triangle', 'Please enter a serial number.'); return; }
        hideStatus();
        showSpinner('Loading applicant information...');
        fetch('/preview', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serial_number: serial }),
        })
            .then(function (r) { return r.json().then(function (d) { return { status: r.status, data: d }; }); })
            .then(function (r) {
                hideSpinner();
                if (r.data.success) {
                    elements.modalBody.innerHTML = r.data.html;
                    elements.modalOverlay.classList.add('show');
                    document.body.style.overflow = 'hidden';
                    hideStatus();
                } else {
                    showStatus('error', 'fas fa-exclamation-circle', r.data.message);
                }
            })
            .catch(function () { hideSpinner(); showStatus('error', 'fas fa-exclamation-circle', 'Failed.'); });
    });

    elements.generateBtn.addEventListener('click', function () {
        var serial = elements.serialInput.value.trim();
        if (!serial) { showStatus('warning', 'fas fa-exclamation-triangle', 'Please enter a serial number.'); return; }
        hideStatus();
        hideDownload();
        showSpinner('Generating PDF...');
        fetch('/generate', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serial_number: serial }),
        })
            .then(function (r) { return r.json().then(function (d) { return { status: r.status, data: d }; }); })
            .then(function (r) {
                hideSpinner();
                if (r.data.success) {
                    showStatus('success', 'fas fa-check-circle', r.data.message);
                    showDownload(r.data.filename);
                } else {
                    showStatus('error', 'fas fa-exclamation-circle', r.data.message);
                }
            })
            .catch(function () { hideSpinner(); showStatus('error', 'fas fa-exclamation-circle', 'Failed.'); });
    });

    function triggerBulkDownload(serials, label) {
        if (!serials.length) { showStatus('warning', 'fas fa-exclamation-triangle', 'No valid serials.'); return; }
        hideStatus();
        hideDownload();
        showSpinner('Generating ' + serials.length + ' PDF' + (serials.length > 1 ? 's' : '') + '...');

        fetch('/generate-bulk', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serials: serials }),
        })
            .then(function (r) {
                if (r.headers.get('content-type') === 'application/json') {
                    return r.json().then(function (d) { return { json: d, blob: null }; });
                }
                return r.blob().then(function (b) { return { json: null, blob: b }; });
            })
            .then(function (r) {
                hideSpinner();
                if (r.json) {
                    showStatus('error', 'fas fa-exclamation-circle', r.json.message || 'Failed.');
                    return;
                }
                var url = URL.createObjectURL(r.blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'hajj_forms.zip';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                showStatus('success', 'fas fa-check-circle', serials.length + ' PDF(s) downloaded successfully.');
            })
            .catch(function () { hideSpinner(); showStatus('error', 'fas fa-exclamation-circle', 'Failed to generate PDFs.'); });
    }

    elements.generateAllBtn.addEventListener('click', function () {
        if (!totalApplicants) { showStatus('warning', 'fas fa-exclamation-triangle', 'No data loaded.'); return; }
        var serials = [];
        for (var i = 1; i <= totalApplicants; i++) { serials.push(i); }
        triggerBulkDownload(serials, 'all');
    });

    elements.generateRangeBtn.addEventListener('click', function () {
        var start = parseInt(elements.rangeStart.value, 10);
        var end = parseInt(elements.rangeEnd.value, 10);
        if (isNaN(start) || isNaN(end) || start < 1 || end < start) {
            showStatus('warning', 'fas fa-exclamation-triangle', 'Enter valid From and To values.');
            return;
        }
        if (end > totalApplicants) { end = totalApplicants; }
        var serials = [];
        for (var i = start; i <= end; i++) { serials.push(i); }
        triggerBulkDownload(serials, 'range');
    });

    elements.generateCustomBtn.addEventListener('click', function () {
        var raw = elements.customSerials.value.trim();
        if (!raw) { showStatus('warning', 'fas fa-exclamation-triangle', 'Enter serial numbers.'); return; }
        var parts = raw.split(',');
        var serials = [];
        parts.forEach(function (p) {
            var n = parseInt(p.trim(), 10);
            if (!isNaN(n) && n > 0) serials.push(n);
        });
        if (!serials.length) { showStatus('warning', 'fas fa-exclamation-triangle', 'No valid serial numbers.'); return; }
        triggerBulkDownload(serials, 'custom');
    });

    function closeModal() {
        elements.modalOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    elements.modalClose.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', function (e) { if (e.target === this) closeModal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && elements.modalOverlay.classList.contains('show')) closeModal(); });
    elements.serialInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); elements.generateBtn.click(); } });
});
