document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        serialInput: document.getElementById('serial-number'),
        previewBtn: document.getElementById('btn-preview'),
        generateBtn: document.getElementById('btn-generate'),
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
    };

    let currentFilename = null;

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
        currentFilename = filename;
        elements.downloadLink.href = '/download/' + encodeURIComponent(filename);
        elements.downloadArea.classList.add('show');
    }

    function hideDownload() {
        currentFilename = null;
        elements.downloadArea.classList.remove('show');
    }

    function updateStatusBadge(loaded, total) {
        elements.statusBadge.classList.toggle('loaded', loaded);
        const dot = elements.statusBadge.querySelector('.status-dot');
        const text = elements.statusBadge.querySelector('.status-text');
        if (loaded) {
            text.textContent = total + ' applicant' + (total !== 1 ? 's' : '') + ' loaded';
        } else {
            text.textContent = 'No data loaded';
        }
    }

    function fetchExcel() {
        showSpinner('Fetching applicant data...');
        fetch('/fetch', { method: 'POST' })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { status: response.status, data: data };
                });
            })
            .then(function (result) {
                hideSpinner();
                if (result.data.success) {
                    updateStatusBadge(true, result.data.total);
                    showStatus('success', 'fas fa-check-circle', result.data.message);
                } else {
                    updateStatusBadge(false, 0);
                    showStatus('error', 'fas fa-exclamation-circle', result.data.message);
                }
            })
            .catch(function () {
                hideSpinner();
                updateStatusBadge(false, 0);
                showStatus('error', 'fas fa-exclamation-circle', 'Failed to fetch applicant data.');
            });
    }

    fetchExcel();

    // Preview button
    elements.previewBtn.addEventListener('click', function () {
        const serial = elements.serialInput.value.trim();
        if (!serial) {
            showStatus('warning', 'fas fa-exclamation-triangle', 'Please enter a serial number.');
            return;
        }

        hideStatus();
        showSpinner('Loading applicant information...');

        fetch('/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serial_number: serial }),
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { status: response.status, data: data };
                });
            })
            .then(function (result) {
                hideSpinner();
                if (result.data.success) {
                    elements.modalBody.innerHTML = result.data.html;
                    elements.modalOverlay.classList.add('show');
                    document.body.style.overflow = 'hidden';
                    hideStatus();
                } else {
                    showStatus('error', 'fas fa-exclamation-circle', result.data.message);
                }
            })
            .catch(function () {
                hideSpinner();
                showStatus('error', 'fas fa-exclamation-circle', 'Failed to load applicant information.');
            });
    });

    // Generate PDF button
    elements.generateBtn.addEventListener('click', function () {
        const serial = elements.serialInput.value.trim();
        if (!serial) {
            showStatus('warning', 'fas fa-exclamation-triangle', 'Please enter a serial number.');
            return;
        }

        hideStatus();
        hideDownload();
        showSpinner('Generating PDF...');

        fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serial_number: serial }),
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { status: response.status, data: data };
                });
            })
            .then(function (result) {
                hideSpinner();
                if (result.data.success) {
                    showStatus('success', 'fas fa-check-circle', result.data.message);
                    showDownload(result.data.filename);
                } else {
                    showStatus('error', 'fas fa-exclamation-circle', result.data.message);
                }
            })
            .catch(function () {
                hideSpinner();
                showStatus('error', 'fas fa-exclamation-circle', 'Failed to generate PDF. Please try again.');
            });
    });

    // Modal close
    function closeModal() {
        elements.modalOverlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    elements.modalClose.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', function (e) {
        if (e.target === this) {
            closeModal();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && elements.modalOverlay.classList.contains('show')) {
            closeModal();
        }
    });

    // Enter key on serial input triggers generate
    elements.serialInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            elements.generateBtn.click();
        }
    });
});
