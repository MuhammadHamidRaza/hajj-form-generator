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
        progressArea: document.getElementById('progress-area'),
        progressFill: document.getElementById('progress-bar-fill'),
        progressText: document.getElementById('progress-text'),
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

    function showProgress(current, total) {
        var pct = total > 0 ? Math.round((current / total) * 100) : 0;
        elements.progressFill.style.width = pct + '%';
        elements.progressText.textContent = 'Generating PDFs... ' + current + '/' + total;
        elements.progressArea.classList.add('show');
    }

    function hideProgress() {
        elements.progressArea.classList.remove('show');
        elements.progressFill.style.width = '0%';
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
        hideProgress();
        showSpinner('Starting generation of ' + serials.length + ' PDF' + (serials.length > 1 ? 's' : '') + '...');

        fetch('/generate-bulk', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serials: serials }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                hideSpinner();
                if (!data.success) {
                    showStatus('error', 'fas fa-exclamation-circle', data.message || 'Failed to start.');
                    return;
                }
                var taskId = data.task_id;
                var total = data.total;
                showProgress(0, total);
                pollTask(taskId, total);
            })
            .catch(function () { hideSpinner(); showStatus('error', 'fas fa-exclamation-circle', 'Failed to start.'); });
    }

    function pollTask(taskId, total) {
        fetch('/task-status/' + taskId)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (!data.success) {
                    hideProgress();
                    showStatus('error', 'fas fa-exclamation-circle', data.message || 'Task failed.');
                    return;
                }
                showProgress(data.progress, total);
                if (data.status === 'done') {
                    hideProgress();
                    if (data.download_url) {
                        var a = document.createElement('a');
                        a.href = data.download_url;
                        a.download = 'hajj_forms.zip';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    }
                    showStatus('success', 'fas fa-check-circle', total + ' PDF(s) downloaded successfully.');
                } else if (data.status === 'error') {
                    hideProgress();
                    showStatus('error', 'fas fa-exclamation-circle', data.message || 'Generation failed.');
                } else {
                    setTimeout(function () { pollTask(taskId, total); }, 800);
                }
            })
            .catch(function () {
                setTimeout(function () { pollTask(taskId, total); }, 1000);
            });
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

    // ===== CNIC Search =====
    var cnicInput = document.getElementById('cnic-input');
    var btnSearchCnic = document.getElementById('btn-search-cnic');
    var cnicResults = document.getElementById('cnic-results');
    var cnicSubTabs = document.querySelectorAll('.cnic-sub-tab');
    var currentCnicMode = 'own';

    cnicSubTabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            cnicSubTabs.forEach(function (t) { t.classList.remove('active'); });
            this.classList.add('active');
            currentCnicMode = this.dataset.cnicMode;
            cnicResults.innerHTML = '';
            hideStatus();
        });
    });

    function renderCnicResults(data) {
        var html = '';
        html += '<div class="cnic-results-header">Found ' + data.count + ' result' + (data.count > 1 ? 's' : '') + '</div>';

        if (data.mode === 'own') {
            var r = data.results[0];
            var a = r.applicant;
            var name = (a['Given Name of Applicant'] || '') + ' ' + (a['Surname of Applicant'] || '');
            html += '<div class="cnic-result-card">';
            html += '<div class="cnic-result-info">';
            html += '<div class="cnic-result-row"><span class="cnic-result-label">Serial #</span><span class="cnic-result-value">' + r.serial_number + '</span></div>';
            html += '<div class="cnic-result-row"><span class="cnic-result-label">Name</span><span class="cnic-result-value">' + name.trim() + '</span></div>';
            html += '<div class="cnic-result-row"><span class="cnic-result-label">CNIC</span><span class="cnic-result-value">' + (a['CNIC No.'] || '—') + '</span></div>';
            html += '<div class="cnic-result-row"><span class="cnic-result-label">Passport</span><span class="cnic-result-value">' + (a['Passport No.'] || '—') + '</span></div>';
            html += '<div class="cnic-result-row"><span class="cnic-result-label">Family #</span><span class="cnic-result-value">' + (a['Family Number'] || '—') + '</span></div>';
            html += '</div>';
            html += '<div class="cnic-result-actions">';
            html += '<button class="btn btn-sm btn-secondary cnic-preview" data-serial="' + r.serial_number + '"><i class="fas fa-eye"></i> Preview</button>';
            html += '<button class="btn btn-sm btn-primary cnic-generate" data-serial="' + r.serial_number + '"><i class="fas fa-file-pdf"></i> Generate</button>';
            html += '</div></div>';
        } else {
            html += '<div class="cnic-family-table"><table><thead><tr><th>#</th><th>Serial</th><th>Name</th><th>Family #</th><th>CNIC</th><th>Action</th></tr></thead><tbody>';
            data.results.forEach(function (r, idx) {
                var a = r.applicant;
                var name = (a['Given Name of Applicant'] || '') + ' ' + (a['Surname of Applicant'] || '');
                html += '<tr>';
                html += '<td>' + (idx + 1) + '</td>';
                html += '<td>' + r.serial_number + '</td>';
                html += '<td>' + name.trim() + '</td>';
                html += '<td>' + (a['Family Number'] || '—') + '</td>';
                html += '<td>' + (a['CNIC No.'] || '—') + '</td>';
                html += '<td><button class="btn btn-sm btn-primary cnic-generate" data-serial="' + r.serial_number + '" style="flex:none;padding:6px 12px;font-size:12px;"><i class="fas fa-file-pdf"></i> PDF</button></td>';
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            var serials = data.results.map(function (r) { return r.serial_number; });
            html += '<button class="btn btn-primary cnic-generate-all" data-serials="' + JSON.stringify(serials) + '" style="margin-top:16px;width:100%;"><i class="fas fa-download"></i> Download All (' + data.count + ' PDFs)</button>';
        }

        cnicResults.innerHTML = html;
        cnicResults.classList.add('show');
    }

    btnSearchCnic.addEventListener('click', function () {
        var cnic = cnicInput.value.trim();
        if (!cnic) { showStatus('warning', 'fas fa-exclamation-triangle', 'Please enter a CNIC number.'); return; }
        hideStatus();
        showSpinner('Searching...');
        fetch('/search-cnic', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cnic: cnic, mode: currentCnicMode }),
        })
            .then(function (r) { return r.json().then(function (d) { return { status: r.status, data: d }; }); })
            .then(function (r) {
                hideSpinner();
                cnicResults.classList.remove('show');
                if (r.data.success) {
                    renderCnicResults(r.data);
                } else {
                    showStatus('error', 'fas fa-exclamation-circle', r.data.message);
                }
            })
            .catch(function () { hideSpinner(); showStatus('error', 'fas fa-exclamation-circle', 'Search failed.'); });
    });

    cnicInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); btnSearchCnic.click(); } });

    document.addEventListener('click', function (e) {
        var previewBtn = e.target.closest('.cnic-preview');
        if (previewBtn) {
            var serial = previewBtn.dataset.serial;
            elements.serialInput.value = serial;
            switchMode('single');
            elements.previewBtn.click();
        }

        var genBtn = e.target.closest('.cnic-generate');
        if (genBtn) {
            var serial = parseInt(genBtn.dataset.serial, 10);
            if (!isNaN(serial)) {
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
            }
        }

        var genAllBtn = e.target.closest('.cnic-generate-all');
        if (genAllBtn) {
            var serials;
            try { serials = JSON.parse(genAllBtn.dataset.serials); } catch (ex) { return; }
            if (serials && serials.length) {
                triggerBulkDownload(serials, 'family');
            }
        }

        // ===== Live Search (PDF from live results) =====
        var liveGenBtn = e.target.closest('.live-generate');
        if (liveGenBtn) {
            var serial = parseInt(liveGenBtn.dataset.serial, 10);
            if (!isNaN(serial)) {
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
            }
        }
    });

    // ===== Live CNIC Search =====
    var liveInput = document.getElementById('live-cnic');
    var liveResults = document.getElementById('live-results');
    var liveTimer = null;

    function renderLiveResults(data) {
        if (!data.count) {
            liveResults.innerHTML = '<div class="live-results-placeholder">No matching applicants found.</div>';
            return;
        }
        var html = '<div class="live-table-wrapper"><table class="live-table"><thead><tr><th>#</th><th>Serial</th><th>Name</th><th>Family #</th><th>CNIC</th><th>Action</th></tr></thead><tbody>';
        data.results.forEach(function (r, idx) {
            var a = r.applicant;
            var name = (a['Given Name of Applicant'] || '') + ' ' + (a['Surname of Applicant'] || '');
            html += '<tr>';
            html += '<td>' + (idx + 1) + '</td>';
            html += '<td>' + r.serial_number + '</td>';
            html += '<td>' + name.trim() + '</td>';
            html += '<td>' + (a['Family Number'] || '—') + '</td>';
            html += '<td>' + (a['CNIC No.'] || '—') + '</td>';
            html += '<td><button class="btn btn-sm btn-primary live-generate" data-serial="' + r.serial_number + '"><i class="fas fa-file-pdf"></i> PDF</button></td>';
            html += '</tr>';
        });
        html += '</tbody></table></div>';
        html += '<p class="live-results-count">Showing ' + data.count + ' result' + (data.count > 1 ? 's' : '') + '</p>';
        liveResults.innerHTML = html;
    }

    function doLiveSearch() {
        var q = liveInput.value.trim();
        if (!q) {
            liveResults.innerHTML = '<div class="live-results-placeholder">Start typing a CNIC number to see results...</div>';
            return;
        }
        fetch('/search-cnic', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cnic: q, mode: 'own', partial: true }),
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    renderLiveResults(data);
                }
            })
            .catch(function () {});
    }

    liveInput.addEventListener('input', function () {
        if (liveTimer) clearTimeout(liveTimer);
        liveTimer = setTimeout(doLiveSearch, 300);
    });
});
